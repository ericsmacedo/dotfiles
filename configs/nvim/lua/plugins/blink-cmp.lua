return {
  "saghen/blink.cmp",
  event = "VimEnter",
  version = "1.*",
  dependencies = {
    "fang2hou/blink-copilot",
    {
      "L3MON4D3/LuaSnip",
      version = "2.*",
      build = function()
        if vim.fn.has("win32") == 1 or vim.fn.executable("make") == 0 then
          return
        end
        return "make install_jsregexp"
      end,
      opts = {},
    },
    "folke/lazydev.nvim",
  },
  opts = {
    keymap = {},
    appearance = {
      nerd_font_variant = "mono",
    },
    completion = {
      keyword = { range = "prefix" },
      documentation = {
        auto_show = true,
        auto_show_delay_ms = 500,
      },
    },
    sources = {
      default = { "lsp", "path", "copilot", "snippets", "lazydev", "buffer" },
      providers = {
        lazydev = {
          module = "lazydev.integrations.blink",
          score_offset = 100,
        },
        copilot = {
          name = "copilot",
          module = "blink-copilot",
          score_offset = 100,
          async = true,
          opts = {
            max_completions = 3,
          },
        },
      },
    },
    snippets = {
      preset = "luasnip",
    },
    fuzzy = {
      implementation = "lua",
    },
    signature = {
      enabled = true,
    },
  },
}
