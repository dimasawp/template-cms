import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Badge from '@/components/ui/Badge.vue'

describe('Badge', () => {
  it('renders with default variant', () => {
    const wrapper = mount(Badge, {
      slots: { default: 'Active' }
    })
    expect(wrapper.text()).toBe('Active')
  })

  it('applies variant class', () => {
    const wrapper = mount(Badge, {
      props: { variant: 'success' },
      slots: { default: 'Done' }
    })
    expect(wrapper.classes()).toContain('bg-green-500/10')
  })
})
