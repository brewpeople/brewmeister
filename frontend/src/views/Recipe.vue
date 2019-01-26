<template>
    <div v-if="recipe">
        <recipe :recipe="recipe" />
        <div>
             <v-btn color="success">Clone</v-btn>
    <v-btn color="warning">Edit</v-btn>
    <v-btn color="info" @click="brew">Brew</v-btn>
        </div>
    </div>
</template>

<script>
import Recipe from '@/components/Recipe'
export default {
    props: {
        recipeId: {
            required: true
        }
    },
    computed: {
        recipe() {
            return this.$store.state.recipes.find(item => item.id === this.recipeId)
        }
    },
    methods: {
        brew() {
            this.$store.commit({
                type: "proposeRecipe",
                recipe: this.recipe
            })
            this.$router.push({
                name: 'process-monitor'
            })
        }
    },
    components: {
        Recipe
    }
}
</script>

<style>

</style>
