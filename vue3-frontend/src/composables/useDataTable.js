import { ref, reactive, watch } from 'vue'

/**
 * Composable for server-side paginated data tables.
 *
 * Usage:
 * ```
 * const { items, isLoading, pagination, search, fetchItems } = useDataTable({
 *   fetchData: async (params) => {
 *     const { data } = await userService.getAll(params)
 *     return { items: data.data.items, total: data.data.pagination.total }
 *   }
 * })
 * ```
 */
export function useDataTable(options) {
  const items = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const search = ref('')
  const filters = reactive({
    search: ''
  })

  const pagination = reactive({
    page: 1,
    perPage: options.perPage || 10,
    total: 0,
    totalPages: 0,
  })

  const sort = reactive(
    options.initialSort || { field: 'id', direction: 'desc' },
  )

  const fetchItems = async () => {
    isLoading.value = true
    error.value = null
    try {
      const params = {
        page: pagination.page,
        per_page: pagination.perPage,
        ...filters,
      }
      if (search.value) params.search = search.value
      if (sort.field) {
        params.order_by = sort.field
        params.order_dir = sort.direction
      }

      const result = await options.fetchData(params)
      items.value = result.items
      pagination.total = result.total
      pagination.totalPages = Math.ceil(result.total / pagination.perPage)
    } catch (err) {
      error.value = err.message || 'Failed to load data'
    } finally {
      isLoading.value = false
    }
  }

  const goToPage = (page) => {
    pagination.page = page
    fetchItems()
  }

  const setSearch = (q) => {
    search.value = q
    pagination.page = 1
    fetchItems()
  }

  const setSortField = (field) => {
    if (sort.field === field) {
      sort.direction = sort.direction === 'asc' ? 'desc' : 'asc'
    } else {
      sort.field = field
      sort.direction = 'asc'
    }
    pagination.page = 1
    fetchItems()
  }

  const setSortDirection = (direction) => {
    sort.direction = direction
    pagination.page = 1
    fetchItems()
  }

  // Debounced search logic for filters
  let debounceTimer
  watch(
    () => ({ ...filters }),
    () => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        pagination.page = 1
        fetchItems()
      }, 500) // 500ms debounce
    },
    { deep: true }
  )

  // Initial fetch
  fetchItems()

  return {
    items, isLoading, error, search, filters,
    pagination, sort,
    fetchItems, goToPage, setSearch, setSortField, setSortDirection,
  }
}
