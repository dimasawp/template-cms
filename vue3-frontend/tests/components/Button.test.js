import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/ui/Button.vue'

describe('Button', () => {
  it('renders with default variant and size', () => {
    const wrapper = mount(Button, {
      slots: { default: 'Click me' }
    })
    expect(wrapper.text()).toBe('Click me')
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('renders with custom variant class', () => {
    const wrapper = mount(Button, {
      props: { variant: 'destructive' },
      slots: { default: 'Delete' }
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('bg-destructive')
  })

  it('disables button when disabled prop is true', () => {
    const wrapper = mount(Button, {
      props: { disabled: true },
      slots: { default: 'Submit' }
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('shows loading spinner when loading', () => {
    const wrapper = mount(Button, {
      props: { loading: true },
      slots: { default: 'Save' }
    })
    expect(wrapper.find('svg').exists()).toBe(true)
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('renders with custom class', () => {
    const wrapper = mount(Button, {
      props: { class: 'my-custom-class' },
      slots: { default: 'Click' }
    })
    expect(wrapper.find('button').classes()).toContain('my-custom-class')
  })
})
