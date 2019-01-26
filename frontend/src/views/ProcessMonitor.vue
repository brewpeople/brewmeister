<template>
    <div>
        <h1>Process Monitor</h1>
        <div v-if="recipeCandidate" class="section">
            <h2>Recipe to start next</h2>
            <div class="recipe-candidate">
                <span class="name">{{ this.recipeCandidate.name }}</span>
                <v-btn color="info" @click="brew(true)">Submit</v-btn>
                <v-btn color="warning" @click="brew(false)">Cancel</v-btn>
            </div>
        </div>
        <div class="section">
            <h2>Current process</h2>
            <v-timeline>
                <v-timeline-item v-for="(stage, n) in stages" :key="n" :color="stage.color()" large>
                    <span slot="opposite"></span>
                    <v-card class="elevation-2">
                        <v-card-title class="headline">{{ stage.name }}</v-card-title>
                        <v-card-text>
                            <line-chart v-if="stage.temps" :data="stage.temps"></line-chart>
                            <v-btn v-if="stage.needsInteraction" color="success" @click="confirm">confirm</v-btn>
                        </v-card-text>
                    </v-card>
                </v-timeline-item>
            </v-timeline>
        </div>
    </div>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'

export default {
  computed: {
    recipeCandidate() {
      return this.$store.state.recipeCandidate;
    },
    stages() {
      return _.get(this, "$store.state.processInfo.stages", []).map(stage => ({
        ...stage,
        color: () => {
          if (_.get(stage, "finished") !== null) {
            return "green";
          }
          if (_.get(stage, "started") !== null ) {
            return "yellow";
          }
          return "red";
        }
      }));
    }
  },
  methods: {
    brew(shouldI) {
      this.$store.dispatch(
        "startBrewProcess",
        shouldI ? this.recipeCandidate : null
      );
    },
    confirm() {
        axios.put(`/control/brew/${this.$store.state.currentBrewId}`, {})
    }
  }
};
</script>

<style lang="scss" scoped>
.section {
  &:not(:last-child) {
    border-bottom: 1px solid lightgray;
  }
}

.recipe-candidate {
  display: flex;
  align-items: center;

  .name {
    font-size: 150%;
    padding: 1em;
  }
}
</style>
