<script setup>
import { ref, onMounted } from 'vue'
import Sortable from 'sortablejs'
import { Pencil, Trash2 } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import StatusIndicator from '@/components/ui/StatusIndicator.vue'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'

const auth = useAuthStore()
const settingsStore = useSettingsStore()

defineOptions({
  name: 'CategoryTreeItem'
})

const props = defineProps({
  categories: {
    type: Array,
    required: true
  },
  depth: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['change', 'edit', 'delete'])

const sortableContainer = ref(null)

onMounted(() => {
  if (sortableContainer.value) {
    Sortable.create(sortableContainer.value, {
      group: 'categories',
      handle: '.drag-handle',
      animation: 150,
      fallbackOnBody: true,
      swapThreshold: 0.65,
      onMove: (evt) => {
        const targetContainer = evt.to;
        const targetDepth = parseInt(targetContainer.getAttribute('data-depth') || '0');
        
        const draggedEl = evt.dragged;
        let maxNesting = 1;
        
        let currentLevel = Array.from(draggedEl.querySelectorAll(':scope > .tree-children-container > .sortable-container > .tree-item-wrapper'));
        while (currentLevel.length > 0) {
          maxNesting++;
          let nextLevel = [];
          currentLevel.forEach(el => {
            const children = Array.from(el.querySelectorAll(':scope > .tree-children-container > .sortable-container > .tree-item-wrapper'));
            nextLevel.push(...children);
          });
          currentLevel = nextLevel;
        }
        
        // Maximum levels deep based on settings
        if (targetDepth + maxNesting > settingsStore.categoryMaxLevel) {
          return false;
        }
        return true;
      },
      onEnd: (evt) => {
        emit('change', evt)
      }
    })
  }
})

function onChange(event) {
  emit('change', event)
}

function handleEdit(cat) {
  emit('edit', cat)
}

function handleDelete(cat) {
  emit('delete', cat)
}
</script>

<template>
  <div class="sortable-container" ref="sortableContainer" :data-depth="depth">
    <div 
      v-for="element in categories" 
      :key="element.id" 
      :data-id="element.id"
      class="tree-item-wrapper border-b border-border last:border-b-0 bg-background hover:bg-muted/30 transition-colors"
    >
      <div class="flex items-center justify-between p-3" :style="{ paddingLeft: `${(depth * 24) + 12}px` }">
        <div class="flex items-center gap-3">
          <div class="drag-handle cursor-move p-1.5 text-muted-foreground hover:text-foreground bg-muted/50 rounded flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="1"/><circle cx="9" cy="5" r="1"/><circle cx="9" cy="19" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="15" cy="5" r="1"/><circle cx="15" cy="19" r="1"/></svg>
          </div>
          
          <span class="font-bold text-primary">{{ element.name }}</span>
          <span class="hidden md:inline text-xs text-muted-foreground">{{ element.slug }}</span>
          
          <Badge v-if="element.is_menu" variant="secondary" class="text-[9px] px-1.5 py-0 h-4">Menu</Badge>
        </div>
        
        <div class="flex items-center gap-4">
          <StatusIndicator :active="element.is_active" />
          
          <div v-if="auth.hasPermission('categories.update') || auth.hasPermission('categories.delete')" class="flex items-center gap-1">
            <button v-if="auth.hasPermission('categories.update')" @click.stop="handleEdit(element)" class="p-1.5 rounded-lg hover:bg-accent transition-colors border border-transparent hover:border-border"><Pencil class="h-4 w-4" /></button>
            <button v-if="auth.hasPermission('categories.delete')" @click.stop="handleDelete(element)" class="p-1.5 rounded-lg hover:bg-accent text-destructive transition-colors border border-transparent hover:border-border"><Trash2 class="h-4 w-4" /></button>
          </div>
        </div>
      </div>

      <div class="border-l-2 border-border/30 ml-7 tree-children-container">
        <CategoryTreeItem 
          v-if="element.children"
          :categories="element.children" 
          :depth="depth + 1"
          @change="onChange"
          @edit="handleEdit"
          @delete="handleDelete"
        />
      </div>
    </div>
  </div>
</template>
