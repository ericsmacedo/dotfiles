return {
  "folke/snacks.nvim",
  priority = 1000,
  lazy = false,
  ---@type snacks.Config
  opts = {
    -- your configuration comes here
    -- or leave it empty to use the default settings
    -- refer to the configuration section below
    indent = { enabled = true },       -- indent guides
    input = { enabled = true },
    dashboard = { enabled = true },    -- dashboard that opens at start-up
    statuscolumn = { enabled = false }, -- prety status column
    notifier = { enabled = true },
    quickfile = { enabled = true },
    scope = { enabled = true },
    scroll = { enabled = true },
    words = { enabled = true },

    picker = { enabled = true },
    explorer = { enabled = true },

    win = {
      preview = { wo = { number = true, relativenumber = true, signcolumn = "no" } },
    },


    toggle = {
      ---@class snacks.toggle.Config
      ---@field icon? string|{ enabled: string, disabled: string }
      ---@field color? string|{ enabled: string, disabled: string }
      ---@field wk_desc? string|{ enabled: string, disabled: string }
      ---@field map? fun(mode: string|string[], lhs: string, rhs: string|fun(), opts?: vim.keymap.set.Opts)
      ---@field which_key? boolean
      ---@field notify? boolean
      {
        map = vim.keymap.set, -- keymap.set function to use
        which_key = true, -- integrate with which-key to show enabled/disabled icons and colors
        notify = true, -- show a notification when toggling
        -- icons for enabled/disabled states
        icon = {
          enabled = " ",
          disabled = " ",
        },
        -- colors for enabled/disabled states
        color = {
          enabled = "green",
          disabled = "yellow",
        },
        wk_desc = {
          enabled = "Disable ",
          disabled = "Enable ",
        },
      }
    },
  }, 

  keys = {
    { "<leader>e", function()
      Snacks.explorer()
      vim.defer_fn(function()
        if vim.bo.filetype == "snacks_picker_list" then  -- replace with actual filetype if different
          vim.wo.relativenumber = true
        end
      end, 100)  -- small delay to ensure buffer is loaded
    end, desc = "File Explorer" },
    { "<leader>n", function()
      if Snacks.config.picker and Snacks.config.picker.enabled then
        Snacks.picker.notifications()
      else
        Snacks.notifier.show_history()
      end
    end, desc = "Notification History" },
    { "<leader>un", function() Snacks.notifier.hide() end, desc = "[D]ismiss All Notifications" },
  },
}


