import { ref, reactive, computed } from 'vue'

export interface SortOption {
  field: string
  direction: 'asc' | 'desc'
}

export interface DataTableOptions<T> {
  fetchData: (params: Record<string, unknown>) => Promise<{ items: T[]; total: number }>
  initialSort?: SortOption
  perPage?: number
}

/**
 * Composable for server-side paginated data tables.
 *
 * Usage:
 * ```
 * const { items, isLoading, pagination, search, fetchItems } = useDataTable<User>({
 *   fetchData: async (params) => {
 *     const { data } = await userService.getAll(params)
 *     return { items: data.data.items, total: data.data.pagination.total }
 *   }
 * })
 * ```
 */
export function useDataTable<T>(options: DataTableOptions<T>) {
  const items = ref<T[]>([]) as any
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const search = ref('')
  const filters = reactive<Record<string, unknown>>({})

  const pagination = reactive({
    page: 1,
    perPage: options.perPage || 10,
    total: 0,
    totalPages: 0,
  })

  const sort = reactive<SortOption>(
    options.initialSort || { field: 'id', direction: 'desc' },
  )

  const fetchItems = async () => {
    isLoading.value = true
    error.value = null
    try {
      const params: Record<string, unknown> = {
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
    } catch (err: any) {
      error.value = err.message || 'Failed to load data'
    } finally {
      isLoading.value = false
    }
  }

  const goToPage = (page: number) => {
    pagination.page = page
    fetchItems()
  }

  const setSearch = (q: string) => {
    search.value = q
    pagination.page = 1
    fetchItems()
  }

  const setSortField = (field: string) => {
    if (sort.field === field) {
      sort.direction = sort.direction === 'asc' ? 'desc' : 'asc'
    } else {
      sort.field = field
      sort.direction = 'asc'
    }
    pagination.page = 1
    fetchItems()
  }

  // Initial fetch
  fetchItems()

  return {
    items, isLoading, error, search, filters,
    pagination, sort,
    fetchItems, goToPage, setSearch, setSortField,
  }
}
