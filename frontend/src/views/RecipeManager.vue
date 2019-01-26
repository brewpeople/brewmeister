<template>
    <div>
        <h1>Recipe list</h1>
        <recipe-preview v-for="recipe in recipes" :key="recipe.id" :recipe="recipe" />
    </div>
</template>

<script>
import RecipePreview from "@/components/RecipePreview";

export default {
    props: {
        recipeId: {
            required: false
        }
    },
  computed: {
    recipes() {
      return this.$store.state.recipes
    }
  },
  components: {
    RecipePreview
  }
};
</script>

<style>
</style>
