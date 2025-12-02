<template>
  <div>
    <h3>Meals</h3>
    <div>
      <input type="date" v-model="dateFilter" @change="fetchMeals" />
    </div>
    <ul>
      <li v-for="m in meals" :key="m.id">
        <strong>{{ m.title }}</strong> — {{ m.time }} — {{ m.total_calories }} kcal
        <button @click="view(m.id)">View</button>
        <button @click="remove(m.id)">Delete</button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from './api'

const dateFilter = ref(new Date().toISOString().slice(0,10))
const meals = ref([])
let token = ''

async function fetchMeals(){
  const data = await apiFetch(`/meals/?date=${dateFilter.value}`, { token })
  meals.value = data.results || data
}

function view(id){ window.location.href = `/meals/${id}` }

async function remove(id){
  const base = import.meta?.env?.VITE_API_BASE || 'http://localhost:8000'
  await fetch(`${base}/meals/${id}/`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } })
  fetchMeals()
}

onMounted(fetchMeals)
</script>

<style scoped>
/* simple styling */
</style>
