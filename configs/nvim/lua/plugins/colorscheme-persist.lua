return {
  "propet/colorscheme-persist.nvim",
  lazy = false, -- Required: Load on startup to set the colorscheme
  config = true, -- Required: call setup() function
  dependencies = {
    "nvim-telescope/telescope.nvim",
    -- NOTE: Add your colorscheme plugins here if you want lazy.nvim
    -- to manage them directly within this plugin specification.
    -- Otherwise, ensure they are installed elsewhere in your config.
    -- Example:
    "folke/tokyonight.nvim",
    "catppuccin/nvim",
  },
  -- Set a keymap to open the picker
  keys = {
    {
      "<leader>pc", -- Or your preferred keymap
      function()
        require("colorscheme-persist").picker()
      end,
      mode = "n",
      desc = "Choose colorscheme",
    },
  },
  -- Optional: Configure the plugin (see Configuration section below)
  opts = {
    -- Add custom options here, for example:
    -- fallback = "space-nvim",
  },
}
