run "if uname | grep -q 'Darwin'; then pgrep spring | xargs kill -9; fi"

# PostgreSQL 17 (this machine runs postgresql@17 on port 5433, alongside an
# older postgresql@15 on the default 5432 for pre-existing apps)
########################################
gsub_file "config/database.yml", "encoding: unicode", "encoding: unicode\n  port: 5433"

# Gemfile
########################################
inject_into_file "Gemfile", before: "group :development, :test do" do
  <<~RUBY
    gem "devise"
    gem 'ruby_llm', '~> 1.15'
  RUBY
end

inject_into_file "Gemfile", after: "group :development, :test do" do
  "\n  gem \"dotenv-rails\""
end

# Flashes
########################################
file "app/views/shared/_flashes.html.erb", <<~HTML
  <% if notice %>
    <div data-controller="flash" class="flex items-center gap-3 px-4 py-3 m-2 rounded-lg bg-blue-50 text-blue-800 text-sm" role="alert">
      <span class="flex-1"><%= notice %></span>
      <button type="button" data-action="click->flash#dismiss" class="text-blue-500 hover:text-blue-700 font-bold" aria-label="Close">&times;</button>
    </div>
  <% end %>
  <% if alert %>
    <div data-controller="flash" class="flex items-center gap-3 px-4 py-3 m-2 rounded-lg bg-yellow-50 text-yellow-800 text-sm" role="alert">
      <span class="flex-1"><%= alert %></span>
      <button type="button" data-action="click->flash#dismiss" class="text-yellow-500 hover:text-yellow-700 font-bold" aria-label="Close">&times;</button>
    </div>
  <% end %>
HTML

# Flash Stimulus controller
########################################
file "app/javascript/controllers/flash_controller.js", <<~JS
  import { Controller } from "@hotwired/stimulus"

  export default class extends Controller {
    static values = { delay: { type: Number, default: 4000 } }

    connect() {
      this.timeout = setTimeout(() => this.dismiss(), this.delayValue)
    }

    disconnect() {
      clearTimeout(this.timeout)
    }

    dismiss() {
      this.element.remove()
    }
  }
JS

inject_into_file "app/views/layouts/application.html.erb", after: "<body>" do
  <<~HTML
    <%= render "shared/flashes" %>
  HTML
end

# README
########################################
markdown_file_content = <<~MARKDOWN
  Rails app generated with [lewagon/rails-templates](https://github.com/lewagon/rails-templates), created by the [Le Wagon coding bootcamp](https://www.lewagon.com) team.
MARKDOWN
file "README.md", markdown_file_content, force: true

# CLAUDE.md
########################################
file "CLAUDE.md", <<~MARKDOWN
  # CLAUDE.md

  This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

  Stack: Ruby #{RUBY_VERSION}, Rails #{Rails::VERSION::STRING}, PostgreSQL 17 (localhost:5433), Tailwind, Propshaft
  <!-- This needs to be changed to reflect project setups -->

  ### Rails conventions and "magic"

  This is a teaching project. For the following Rails conventions, always explain what is happening and show the equivalent explicit code:

  - **`resources`** — what routes it generates and what each maps to
  - **Member routes** — what `member do` adds and how it differs from a plain `get`
  - **Collection routes** — same treatment as member routes
  - **Implicit template lookup** — when a controller action renders without an explicit `render` call, explain which file Rails finds and why

  ### Branch context

  At the start of any work on a branch, check the branch name for an issue number. If one is present (e.g. `feature/42-add-reviews`), run `gh issue view <number>` and use the title, description, and comments as context before starting.

  ### Commits

  While working on a branch, suggest good moments to commit and briefly explain why it is a natural checkpoint (e.g. a feature is working, a refactor is complete, tests pass, a logical unit of work is done).

  ### Refactoring

  When making a refactor, always explain what is changing and why it is beneficial before making the change.

  ### Spec-driven changes

  Non-trivial changes go through OpenSpec: `/opsx:propose "..."` to draft a change proposal,
  `/opsx:apply` to implement an approved one. See `openspec/` for current specs and in-flight
  changes.

  ## JavaScript

  Two patterns are available, both loaded via import maps — no bundler, no build step:
  - **Stimulus controllers** — behavior wired to server-rendered/Turbo-updated DOM (forms,
    `data-*` attributes, reacting to Turbo events). Default for anything tied to a specific view.
  - **Web Components (native Custom Elements)** — self-contained widgets that own their state
    and rendering, independent of the surrounding page. Reach for this when a piece of UI
    doesn't need Rails-rendered data attributes to function.

  No inline scripts or bare `addEventListener` calls outside a controller or component. See
  `app/javascript/CLAUDE.md` for conventions and examples of each.
MARKDOWN

# app/javascript/CLAUDE.md
########################################
file "app/javascript/CLAUDE.md", <<~MARKDOWN
  # JavaScript — Stimulus & Web Component conventions

  Two patterns are available, both loaded via import maps — no bundler, no build step. Pick one
  per widget, don't mix within it:

  - **Stimulus controllers** — behavior wired to server-rendered or Turbo-updated DOM: forms,
    `data-*` attributes, reacting to Turbo events, manipulating elements Rails rendered. Default
    for anything tied to a specific view/controller.
  - **Web Components (native Custom Elements)** — self-contained, reusable widgets that own
    their state and rendering, independent of the surrounding page. Reach for this when a piece
    of UI doesn't need Rails-rendered data attributes to function (e.g. a countdown timer, a
    copy-to-clipboard button, a client-side-only chart).

  No inline scripts, no bare `addEventListener` calls outside a controller or component.

  ## Stimulus controllers

  1. Add `app/javascript/controllers/<name>_controller.js` — auto-loaded by `controllers/index.js`.
  2. Wire it up in HTML with `data-controller="<name>"`.

  ```js
  import { Controller } from "@hotwired/stimulus"

  export default class extends Controller {
    static targets = ["input"]   // → this.inputTarget / this.inputTargets
    static values  = { url: String }  // → this.urlValue

    connect() { /* called when element enters the DOM */ }
    disconnect() { /* cleanup */ }
  }
  ```

  | Purpose | Attribute |
  |---|---|
  | Mount controller | `data-controller="name"` |
  | Declare a target | `data-name-target="targetName"` |
  | Bind an action | `data-action="click->name#method"` |
  | Pass a value | `data-name-url-value="<%= some_path %>"` |

  Default event per element (`input`→`input`, `form`→`submit`, `a/button`→`click`) can be omitted: `data-action="name#method"`.

  ## Web Components

  Not scaffolded by default — this is the convention to follow the first time one is needed.

  1. Add `app/javascript/elements/<name>_element.js`, defining and registering the element:

     ```js
     class CopyButtonElement extends HTMLElement {
       connectedCallback() {
         this.addEventListener("click", () => navigator.clipboard.writeText(this.dataset.text))
       }
     }

     customElements.define("copy-button", CopyButtonElement)
     ```

  2. Pin the directory in `config/importmap.rb`, alongside the existing `controllers` pin:
     ```ruby
     pin_all_from "app/javascript/elements", under: "elements"
     ```
  3. Import it once, as a side effect, from `app/javascript/application.js`:
     ```js
     import "elements/copy_button_element"
     ```
  4. Use it directly in views, no `data-controller` needed: `<copy-button data-text="...">Copy</copy-button>`.

  ## Adding an external library

  1. Pin it in `config/importmap.rb`:
     ```ruby
     pin "library-name", to: "https://cdn.example.com/library.esm.js"
     ```
  2. Import it inside the controller or component that needs it — not globally.
MARKDOWN

# app/views/CLAUDE.md
########################################
file "app/views/CLAUDE.md", <<~MARKDOWN
  # Views — styling conventions

  Use Tailwind utility classes first. Only write custom CSS when the utility classes genuinely can't achieve the result.

  When working on views, suggest extracting repeated or self-contained chunks into partials if it would genuinely improve clarity. Only flag it when the view would be meaningfully easier to read or reuse as a result.
MARKDOWN

# Generators
########################################
generators = <<~RUBY
  config.generators do |generate|
    generate.assets false
    generate.helper false
    generate.test_framework :test_unit, fixture: false
  end
RUBY

environment generators

########################################
# After bundle
########################################
after_bundle do
  # Generators: db + simple form + pages controller
  ########################################
  rails_command "db:drop db:create db:migrate"
  generate(:controller, "pages", "home", "--skip-routes", "--no-test-framework")

  # Routes
  ########################################
  route 'root to: "pages#home"'

  # Gitignore
  ########################################
  append_file ".gitignore", <<~TXT
    # Ignore .env file containing credentials.
    .env*

    # Ignore Mac and Linux file system files
    *.swp
    .DS_Store
  TXT

  # Devise install + user
  ########################################
  generate("devise:install")
  generate("devise", "User")

  # Application controller
  ########################################
  run "rm app/controllers/application_controller.rb"
  file "app/controllers/application_controller.rb", <<~RUBY
    class ApplicationController < ActionController::Base
      before_action :authenticate_user!
    end
  RUBY

  # migrate + devise views
  ########################################
  rails_command "db:migrate"
  generate("devise:views")

  link_to = <<~HTML
    <p>Unhappy? <%= link_to "Cancel my account", registration_path(resource_name), data: { confirm: "Are you sure?" }, method: :delete %></p>
  HTML
  button_to = <<~HTML
    <div class="flex items-center gap-2">
      <span>Unhappy?</span>
      <%= button_to "Cancel my account", registration_path(resource_name), data: { confirm: "Are you sure?" }, method: :delete, class: "text-sm text-red-600 hover:text-red-800 hover:underline" %>
    </div>
  HTML
  gsub_file("app/views/devise/registrations/edit.html.erb", link_to, button_to)

  # Pages Controller
  ########################################
  run "rm app/controllers/pages_controller.rb"
  file "app/controllers/pages_controller.rb", <<~RUBY
    class PagesController < ApplicationController
      skip_before_action :authenticate_user!, only: [ :home ]

      def home
      end
    end
  RUBY

  # Single Database Setup (Solid Cable, Queue, Cache)
  ########################################
  rails_command "generate migration InstallSolidCable"
  rails_command "generate migration InstallSolidQueue"
  rails_command "generate migration InstallSolidCache"

  ["cable", "queue", "cache"].each do |name|
    schema_file = "db/#{name}_schema.rb"
    migration_file = Dir["db/migrate/*_install_solid_#{name}.rb"].first
    next unless migration_file && File.exist?(schema_file)

    lines = File.readlines(schema_file)
    start_idx = lines.index { |l| l.match?(/\.define.*do/) }
    next unless start_idx

    inner_content = lines[(start_idx + 1)..-2]
                      .map { |l| l == "\n" ? l : "  #{l}" }
                      .join

    gsub_file migration_file, "  def change\n  end", "  def change\n#{inner_content}  end"
  end

  rails_command "db:migrate"

  remove_file "db/queue_schema.rb"
  remove_file "db/cache_schema.rb"

  new_production_db_config = <<~YAML
    production:
      primary:
        <<: *default
        url: <%= ENV["DATABASE_URL"] %>
      cache:
        <<: *default
        url: <%= ENV["DATABASE_URL"] %>
      queue:
        <<: *default
        url: <%= ENV["DATABASE_URL"] %>
      cable:
        <<: *default
        url: <%= ENV["DATABASE_URL"] %>
  YAML
  gsub_file "config/database.yml", /^production:.*\z/m, new_production_db_config

  # Environments
  ########################################
  environment 'config.action_mailer.default_url_options = { host: "http://localhost:3000" }', env: "development"
  environment 'config.action_mailer.default_url_options = { host: "http://TODO_PUT_YOUR_DOMAIN_HERE" }',
              env: "production"

  # Heroku
  ########################################
  run "bundle lock --add-platform x86_64-linux"

  # Dotenv
  ########################################
  run "touch '.env'"

  # Rubocop
  ########################################
  run "curl -L https://raw.githubusercontent.com/lewagon/rails-templates/master/.rubocop.yml > .rubocop.yml"

  # CI
  ########################################
  remove_file ".github/workflows/ci.yml"

  # OpenSpec (spec-driven change workflow for Claude Code)
  ########################################
  run "openspec init --tools claude --force"

  # Git
  ########################################
  git :init
  git add: "."
  git commit: "-m 'Initial commit with devise template from https://github.com/lewagon/rails-templates'"
end