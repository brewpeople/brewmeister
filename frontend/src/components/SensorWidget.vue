<template>
    <div v-if="readings" class="wrapper">
        <span>{{ readings.temps.wort | temperature }}</span>
        <div @click="toggle('valve')">
            <v-icon v-if="readings.states.valve" color="success">flash_on</v-icon>
        <v-icon v-else color="error">flash_off</v-icon>
        </div>
        
        <div @click="toggle('stirrer')">
            <v-icon v-if="readings.states.stirrer" color="success">loop</v-icon>
            <v-icon v-else color="error">not_interested</v-icon>
        </div>

    </div>
    <div v-else>
        <span>(not connected)</span>
    </div>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'

export default {
  props: {
    readings: {
      required: true
    }
  },
  methods: {
      toggle(what) {
          const current = _.get(this, ['readings', 'states', what], true)
          const desired = !current
          axios.put(`/control/switch/${what}`, {
              on: desired
          })
      }
  }
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  align-items: center;
}
</style>
