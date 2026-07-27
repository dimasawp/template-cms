import {
  FileText,
  FolderTree
} from 'lucide-vue-next'

/**
 * EXTENSION MODULES CONFIGURATION
 * 
 * To disable a module from the UI (Sidebar), simply comment it out or remove it from this array.
 * Note: You still need to remove its route from `src/router/index.js` if you want to completely remove it from the Vue bundle.
 */
export const extensionModules = [
  {
    name: 'Posts',
    group: 'Web Content',
    icon: FileText,
    route: '/posts',
    permission: 'posts.view'
  },
  {
    name: 'Categories',
    group: 'Web Content',
    icon: FolderTree,
    route: '/categories',
    permission: 'categories.view'
  }
]
