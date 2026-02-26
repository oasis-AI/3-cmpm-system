import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePointsStore = defineStore('points', () => {
  const balance = ref<number>(0)
  const recentRecords = ref<any[]>([])

  function setBalance(n: number) {
    balance.value = n
  }

  function setRecentRecords(records: any[]) {
    recentRecords.value = records
  }

  function deduct(n: number) {
    balance.value = Math.max(0, balance.value - n)
  }

  function add(n: number) {
    balance.value += n
  }

  return { balance, recentRecords, setBalance, setRecentRecords, deduct, add }
})
