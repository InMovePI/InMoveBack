<template>
  <div v-if="meal">
    <h2>{{ meal.title }}</h2>
    <p>{{ meal.date }} {{ meal.time }}</p>
    <ul>
      <li v-for="i in meal.ingredients" :key="i.id">
        {{ i.food_name }} — {{ i.weight_grams }}g — {{ i.calories }} kcal
      </li>
    </ul>
    <div>Totals: {{ meal.total_calories }} kcal</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from './api'
import { useRoute } from 'vue-router'

const meal = ref(null)
const route = useRoute()
let token = ''

onMounted(async ()=>{
  const id = route.params.id
  meal.value = await apiFetch(`/meals/${id}/`, { token })
})
</script>

<style scoped></style>
