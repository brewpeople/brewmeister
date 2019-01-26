import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import RecipeManager from './views/RecipeManager'
import HelperWidgets from './views/HelperWidgets'
import ProcessMonitor from './views/ProcessMonitor'
import Recipe from './views/Recipe'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/recipes',
      name: 'recipes',
      component: RecipeManager,
      props: route => ({
        recipeId: route.params.recipeId
      })
    },
    {
      path: '/recipes/:recipeId',
      name: 'recipe',
      component: Recipe,
      props: route => ({
        recipeId: route.params.recipeId
      })
    },
    {
      path: '/widgets',
      name: 'widgets',
      component: HelperWidgets
    },
    {
      path: '/process-monitor',
      name: 'process-monitor',
      component: ProcessMonitor
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import(/* webpackChunkName: "about" */ './views/About.vue')
    }
  ]
})
