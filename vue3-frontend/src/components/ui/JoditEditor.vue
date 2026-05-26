<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { Jodit } from 'jodit'
import 'jodit/esm/plugins/all.js'
import 'jodit/es2021/jodit.min.css'

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
          a.setAttribute('class', 'text-primary font-bold hover:underline')
          a.textContent = '📄 Download ' + filename
          this.s.insertNode(a)
        }
      },
      defaultHandlerError: function (err) {
        this.events.fire('errorMessage', 'Gagal mengupload file: ' + (err.message || 'Error server'))
      }
    },
    buttons: ['source', '|', 'bold', 'strikethrough', 'underline', 'italic', '|', 'superscript', 'subscript', '|', 'ul', 'ol', '|', 'outdent', 'indent', '|', 'font', 'fontsize', 'brush', 'paragraph', '|', 'image', 'video', 'file', 'table', 'link', '|', 'align', 'undo', 'redo', '\n', 'hr', 'eraser', 'copyformat', '|', 'symbol', 'fullsize', 'print', 'preview', 'about', 'speechRecognize'],
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
  <textarea ref="editorRef"></textarea>
</template>
