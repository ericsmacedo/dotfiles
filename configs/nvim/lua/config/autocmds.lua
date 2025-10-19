--  See `:help lua-guide-autocommands`

-- Highlight when yanking (copying) text
--  Try it with `yap` in normal mode
--  See `:help vim.hl.on_yank()`
vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking (copying) text',
  group = vim.api.nvim_create_augroup('kickstart-highlight-yank', { clear = true }),
  callback = function()
    vim.hl.on_yank()
  end,
})

-- [[ Install `lazy.nvim` plugin manager ]]
--    See `:help lazy.nvim.txt` or https://github.com/folke/lazy.nvim for more info
local lazypath = vim.fn.stdpath 'data' .. '/lazy/lazy.nvim'
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local lazyrepo = 'https://github.com/folke/lazy.nvim.git'
  local out = vim.fn.system { 'git', 'clone', '--filter=blob:none', '--branch=stable', lazyrepo, lazypath }
  if vim.v.shell_error ~= 0 then
    error('Error cloning lazy.nvim:\n' .. out)
  end
end

-- "===================================================================
-- " CUSTOM INDENTATION
-- "===================================================================
local set_rtl_ident = function()
    vim.o.tabstop = 3          -- number of spaces in tab when editing
    vim.o.softtabstop = 3      -- number of spaces in tab when editing.
    vim.o.shiftwidth = 3       -- number of spaces used for >> and <<
    vim.o.expandtab = true     -- tabs are spaces
end

local set_ident_2 = function()
    vim.o.tabstop = 2          -- number of spaces in tab when editing
    vim.o.softtabstop = 2      -- number of spaces in tab when editing.
    vim.o.shiftwidth = 2       -- number of spaces used for >> and <<
    vim.o.expandtab = true     -- tabs are spaces
end

vim.api.nvim_create_autocmd({"BufNewFile", "BufRead"},
                            {pattern = {"*.sv"},
                             callback = set_rtl_ident
                            })

vim.api.nvim_create_autocmd({"BufNewFile", "BufRead"},
                            {pattern = {"*.yml", "*.html", "*.lua"},
                             callback = set_ident_2
                            })
