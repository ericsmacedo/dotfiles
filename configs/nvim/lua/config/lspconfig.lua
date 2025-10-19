
local servers = { "ruff", "jedi_language_server", "lua_ls"}
vim.lsp.enable(servers)

vim.lsp.config('ruff', {
  init_options = {
    settings = {
      -- Ruff language server settings go here
    }
  }
})

vim.lsp.config('pylsp', {
  cmd = {vim.call("expand", "~/.config/nvim/.venv/bin/pylsp")},
  settings = {
    pylsp = {
      plugins = {
        pycodestyle = {
          ignore = {'E226'},
          maxLineLength = 88
        }
      }
    }
  }
})

vim.lsp.config('jedi_language_server', {
  cmd = {vim.call("expand", "~/.config/nvim/.venv/bin/jedi-language-server")},
})

vim.lsp.config('lua_ls', {
  -- cmd = { ... },
  -- filetypes = { ... },
  -- capabilities = {},
  settings = {
    Lua = {
      completion = {
        callSnippet = 'Replace',
      },
      -- You can toggle below to ignore Lua_LS's noisy `missing-fields` warnings
      -- diagnostics = { disable = { 'missing-fields' } },
    },
  },
})

