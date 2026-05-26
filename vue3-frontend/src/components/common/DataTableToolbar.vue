<script setup>
import { Search, RotateCw, Plus } from 'lucide-vue-next'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'

defineProps(['searchModelValue', 'searchPlaceholder', 'isLoading', 'showAddButton', 'addButtonLabel'])

defineEmits(['update:searchModelValue', 'add', 'refresh'])
</script>

<template>
  <div class="flex flex-col gap-4 mb-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <!-- Search & Refresh -->
      <div class="flex flex-1 items-center gap-3 max-w-xl">
        <div class="relative flex-1 group">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <Input 
            :model-value="searchModelValue"
            @update:model-value="v => $emit('update:searchModelValue', v)"
            :placeholder="searchPlaceholder || 'Cari data...'" 
            class="pl-10 h-10 border-input bg-background focus:border-primary focus:ring-primary/20 shadow-sm"
          />
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          class="h-10 px-3 border-input shadow-sm" 
          @click="$emit('refresh')" 
          :disabled="isLoading"
        >
          <RotateCw class="h-4 w-4" :class="{'animate-spin': isLoading}" />
        </Button>
      </div>

      <!-- Actions (Filters, Sort, Buttons) -->
      <div class="flex items-center gap-2">
        <!-- Slots for Filter and Sort buttons to maintain their own popover state -->
        <slot name="actions-start" />
        
        <slot name="actions-end">
          <Button 
            v-if="showAddButton"
            type="primary" 
            class="h-10 px-4 shadow-md bg-primary hover:bg-primary/90 transition-all font-bold"
            @click="$emit('add')"
          >
            <Plus class="mr-2 h-4 w-4" />
            {{ addButtonLabel || 'Tambah Data' }}
          </Button>
        </slot>
      </div>
    </div>
    
    <!-- Optional bar if needed -->
    <slot name="bottom" />
  </div>
</template>
