<template>
  <div>
    <h3>Weekly Summary</h3>
    <table>
      <thead><tr><th>Day</th><th>Calories</th><th>Protein</th><th>Carbs</th><th>Fat</th></tr></thead>
      <tbody>
        <tr v-for="(v,k) in days" :key="k">
          <td>{{ k }}</td>
          <td>{{ v.calories }}</td>
          <td>{{ v.protein }}</td>
          <td>{{ v.carbs }}</td>
          <td>{{ v.fat }}</td>
        </tr>
      </tbody>
    </table>
    <div>Week totals: {{ week_totals.calories }} kcal</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from './api'

const days = ref({})
const week_totals = ref({calories:0,protein:0,carbs:0,fat:0})
let token = ''

onMounted(async ()=>{
  const data = await apiFetch('/meals/weekly-summary/', { token })
  days.value = data.days
  week_totals.value = data.week_totals
})
</script>

<style scoped></style>
