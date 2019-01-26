import Vue from 'vue'
import Vuex from 'vuex'

import axios from 'axios'
import _ from 'lodash'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    recipes: [],
    processInfo: undefined,
    brews: [],
    sensors: undefined,
    recipeCandidate: undefined,
    currentBrewId: undefined
  },
  mutations: {
    updateRecipes(state, { recipes }) {
      state.recipes = recipes
    },
    updateSensors(state, { sensors }) {
      state.sensors = sensors
    },
    updateProcessInfo(state, { processInfo }) {
      state.processInfo = processInfo
    },
    proposeRecipe(state, { recipe }) {
      state.recipeCandidate = recipe
    },
    updateField(state, { field, value }) {
      state[field] = value
    }
  },
  actions: {
    async updateRecipes({ commit }) {
      const recipes = (await axios.get('/recipes')).data
      commit({
        type: 'updateRecipes',
        recipes
      })
    },
    async updateBrews({ commit }) {
      const response = await axios.get('/control/bews').catch(_.noop)

    },
    async updateSensors({ commit }) {
      const sensors = (await axios.get('/control/sensors')).data
      commit({
        type: 'updateSensors',
        sensors
      })
    },
    async updateProcessInfo({ state, commit }) {
      if (state.currentBrewId) {
        const response = await axios.get(`/control/brew/${state.currentBrewId}`).catch(_.noop)
        commit({
          type: 'updateProcessInfo',
          processInfo: _.get(response, 'data')
        })
      }
    },
    async startBrewProcess({ commit }, recipe) {
      if (!recipe) {
        commit({
          type: 'proposeRecipe',
          recipe: null
        })
      } else {
        const response = await axios.post('/control/brew', recipe)
        commit({
          type: 'updateField',
          field: 'currentBrewId',
          value: _.get(response, 'data.id')
        })
      }
    }
  }
})
