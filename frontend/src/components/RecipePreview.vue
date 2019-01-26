<template>
    <div>
        <h2>{{ recipe.name }}</h2>
        <router-link :to="{ name: 'recipe', params: { recipeId: recipe.id } }">visit</router-link>
    </div>
</template>

<script>
export default {
    props: {
        recipe: {
            required: true
        }
    }

}
</script>

<style>

</style>
