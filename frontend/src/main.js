import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// vuetify
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import 'material-design-icons-iconfont'

import VueChartkick from 'vue-chartkick'
import Chart from 'chart.js'

Vue.use(VueChartkick, { adapter: Chart })

Vue.use(Vuetify)

Vue.config.productionTip = false

Vue.filter('temperature', function (value) {
  return `${value.toFixed(1)} °C`
})

setInterval(() => {
  store.dispatch('updateSensors')
  store.dispatch('updateProcessInfo')
}, 2000)

store.dispatch('updateRecipes')

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
