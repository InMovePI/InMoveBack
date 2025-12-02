<template>
  <form @submit.prevent="onSubmit">
    <label>Title <input v-model="title" required/></label>
    <label>Date <input type="date" v-model="date" required/></label>
    <label>Time <input type="time" v-model="time" required/></label>

    <div v-for="(ing, idx) in ingredients" :key="idx" class="ingredient">
      <input v-model="ing.query" @input="onQueryChange(idx)" placeholder="Buscar alimento..." />
      <ul v-if="ing.suggestions.length">
        <li v-for="s in ing.suggestions" :key="s.id" @click="selectSuggestion(idx, s)">{{ s.name }} ({{ s.nutrients.calories }} kcal/100g)</li>
      </ul>
      <input type="number" v-model.number="ing.weight_grams" @input="recalc(idx)" min="1"/> g
      <div class="macros">Cal: {{ ing.macros.calories }} | P: {{ ing.macros.protein }} | C: {{ ing.macros.carbs }} | F: {{ ing.macros.fat }}</div>
      <button type="button" @click="removeIngredient(idx)">Remove</button>
    </div>

    <button type="button" @click="addIngredient">Add ingredient</button>
    <button type="submit">Create Meal</button>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { searchFoods, createMeal } from './api'

const title = ref('')
const date = ref(new Date().toISOString().slice(0,10))
const time = ref('08:30')

const ingredients = ref([{ query: '', weight_grams: 100, suggestions: [], selected: null, macros: { calories:0, protein:0, carbs:0, fat:0 } }])

let token = '' // fill with logged in token

function addIngredient(){ ingredients.value.push({ query:'', weight_grams:100, suggestions:[], selected: null, macros:{calories:0,protein:0,carbs:0,fat:0} }) }
function removeIngredient(i){ ingredients.value.splice(i,1) }

let debounceTimers = {}
function onQueryChange(i){
  const q = ingredients.value[i].query
  clearTimeout(debounceTimers[i])
  debounceTimers[i] = setTimeout(async ()=>{
    if (!q) { ingredients.value[i].suggestions = []; return }
    const results = await searchFoods(q, 'BR','pt', token)
    ingredients.value[i].suggestions = results
  }, 300)
}

function selectSuggestion(i, s){
  ingredients.value[i].selected = s
  ingredients.value[i].query = s.name
  ingredients.value[i].suggestions = []
  recalc(i)
}

function recalc(i){
  const ing = ingredients.value[i]
  const grams = Number(ing.weight_grams) || 0
  if (ing.selected){
    const scale = grams / (ing.selected.weight_grams || 100)
    ing.macros.calories = Math.round((ing.selected.nutrients.calories || 0) * scale*100)/100
    ing.macros.protein = Math.round((ing.selected.nutrients.protein || 0) * scale*100)/100
    ing.macros.carbs = Math.round((ing.selected.nutrients.carbs || 0) * scale*100)/100
    ing.macros.fat = Math.round((ing.selected.nutrients.fat || 0) * scale*100)/100
  } else {
    ing.macros = {calories:0,protein:0,carbs:0,fat:0}
  }
}

async function onSubmit(){
  const payload = {
    title: title.value,
    date: date.value,
    time: time.value + ':00',
    ingredients: ingredients.value.map(i=>({ food_name: i.selected ? i.selected.id : i.query, weight_grams: i.weight_grams }))
  }
  await createMeal(payload, token)
  alert('Meal created')
}
</script>

<style scoped>
.ingredient{margin-bottom:8px}
.macros{font-size:smaller;color:#666}
</style>
