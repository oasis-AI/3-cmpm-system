import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const count = ref<number>(0)

  function setCount(n: number) {
    count.value = n
  }

  function increment() {
    count.value++
  }

  function decrement(n = 1) {
    count.value = Math.max(0, count.value - n)
  }

  function reset() {
    count.value = 0
  }

  return { count, setCount, increment, decrement, reset }
})
