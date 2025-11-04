-- This plugin allow me to navigate between tmux windows and nvim windows using ctrl keys
return {
  "alexghergh/nvim-tmux-navigation",
  config = function()
    local nvim_tmux_nav = require("nvim-tmux-navigation")
    vim.keymap.set('n', '<C-h>', nvim_tmux_nav.NvimTmuxNavigateLeft, { desc = 'Tmux Navigate Left' })
    vim.keymap.set('n', '<C-j>', nvim_tmux_nav.NvimTmuxNavigateDown, { desc = 'Tmux Navigate Down' })
    vim.keymap.set('n', '<C-k>', nvim_tmux_nav.NvimTmuxNavigateUp, { desc = 'Tmux Navigate Up' })
    vim.keymap.set('n', '<C-l>', nvim_tmux_nav.NvimTmuxNavigateRight, { desc = 'Tmux Navigate Right' })
    -- vim.keymap.set('n', '<C-\\>', nvim_tmux_nav.NvimTmuxNavigateLastActive, { desc = 'Tmux Navigate Last Active' })
    -- vim.keymap.set('n', '<C-Space>', nvim_tmux_nav.NvimTmuxNavigateNext, { desc = 'Tmux Navigate Next' })
  end,
}
