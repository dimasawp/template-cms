<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { Jodit } from 'jodit'
import 'jodit/esm/plugins/all.js'
import 'jodit/es2021/jodit.min.css'
import MediaManagerModal from '@/components/common/MediaManagerModal.vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  config: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

import { useTheme } from '@/composables/useTheme'
const { isDark } = useTheme()

const editorRef = ref(null)
let editorInstance = null

const isMediaModalOpen = ref(false)

const insertMedia = (url) => {
  if (!editorInstance) return
  
  // Clean URL to check extension ignoring query params
  const cleanUrl = url.split('?')[0]
  const ext = cleanUrl.split('.').pop().toLowerCase()
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp']
  
  if (imageExts.includes(ext)) {
    editorInstance.s.insertImage(url, null, '100%')
  } else {
    const filename = cleanUrl.split('/').pop() || 'File'
    const a = editorInstance.createInside.element('a')
    a.setAttribute('href', url)
    a.setAttribute('target', '_blank')
    a.setAttribute('style', 'color: #2563eb; text-decoration: underline; font-weight: bold;')
    a.textContent = '📄 Download ' + filename
    editorInstance.s.insertNode(a)
  }
}

onMounted(() => {
  editorInstance = Jodit.make(editorRef.value, {
    textIcons: false,
    theme: isDark.value ? 'dark' : 'default',
    cleanHTML: {
      fillEmptyParagraph: false,
      removeEmptyElements: false,
      allowTags: 'iframe,video,audio,source,embed,object,p,div,span,h1,h2,h3,h4,h5,h6,ul,ol,li,a,img,table,tr,td,th,tbody,thead,tfoot,b,strong,i,em,u,s,strike,br,hr,blockquote,pre,code'
    },
    height: 'auto',
    minHeight: 400,
    imageDefaultWidth: '100%',
    uploader: {
      url: (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1') + '/media/upload',
      format: 'json',
      insertImageAsBase64URI: false,
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('access_token')
      },
      isSuccess: function (resp) {
        return resp.status === 'success';
      },
      process: function (resp) {
        return {
          files: [resp.data.path],
          path: resp.data.path,
          original_name: resp.data.original_name,
          baseurl: (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace('/api/v1', '') + '/',
          error: 0,
          message: resp.message
        };
      },
      defaultHandlerSuccess: function (data) {
        let url = data.files[0]
        if (!url.startsWith('http')) {
          url = data.baseurl + url
        }
        
        const ext = url.split('.').pop().toLowerCase()
        const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp']
        
        if (imageExts.includes(ext)) {
          this.s.insertImage(url, null, this.o.imageDefaultWidth)
        } else {
          const filename = data.original_name || url.split('/').pop()
          const a = this.createInside.element('a')
          a.setAttribute('href', url)
          a.setAttribute('target', '_blank')
          a.setAttribute('style', 'color: #2563eb; text-decoration: underline; font-weight: bold;')
          a.textContent = '📄 Download ' + filename
          this.s.insertNode(a)
        }
      },
      defaultHandlerError: function (err) {
        this.events.fire('errorMessage', 'Gagal mengupload file: ' + (err.message || 'Error server'))
      }
    },
    extraButtons: [
      {
        name: 'mediaLibrary',
        iconURL: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-image"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>',
        tooltip: 'Select from Media Library',
        exec: (editor) => {
          isMediaModalOpen.value = true
        }
      }
    ],
    buttons: ['mediaLibrary', '|', 'source', '|', 'bold', 'strikethrough', 'underline', 'italic', '|', 'superscript', 'subscript', '|', 'ul', 'ol', '|', 'outdent', 'indent', '|', 'font', 'fontsize', 'brush', 'paragraph', '|', 'image', 'video', 'file', 'table', 'link', '|', 'align', 'undo', 'redo', '\n', 'hr', 'eraser', 'copyformat', '|', 'symbol', 'fullsize', 'print', 'preview', 'about'],
    ...props.config
  })
  
  editorInstance.value = props.modelValue
  
  editorInstance.events.on('change', newValue => {
    emit('update:modelValue', newValue)
  })
})

watch(() => props.modelValue, (newValue) => {
  if (editorInstance && editorInstance.value !== newValue) {
    editorInstance.value = newValue
  }
})

onBeforeUnmount(() => {
  if (editorInstance) {
    editorInstance.destruct()
  }
})
</script>

<template>
  <div class="jodit-wrapper">
    <textarea ref="editorRef"></textarea>
    <MediaManagerModal 
      :open="isMediaModalOpen" 
      mode="select" 
      @close="isMediaModalOpen = false" 
      @select="insertMedia" 
    />
  </div>
</template>
