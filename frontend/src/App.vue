<template>
  <v-app id="keep">
    <v-navigation-drawer v-model="drawer" fixed clipped class="grey lighten-4" app>
      <v-list dense class="grey lighten-4">
        <template v-for="(item, i) in items">
          <v-layout v-if="item.heading" :key="i" row align-center>
            <v-flex xs6>
              <v-subheader v-if="item.heading">
                {{ item.heading }}
              </v-subheader>
            </v-flex>
          </v-layout>
          <v-divider v-else-if="item.divider" :key="i" dark class="my-3"></v-divider>
          <v-list-tile v-else-if="item.to" :key="i" @click="$router.push({
              name: item.to
            })">
            <v-list-tile-action>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title class="grey--text">
                {{ item.text }}
              </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </template>
      </v-list>
    </v-navigation-drawer>
    <v-toolbar color="amber" app absolute clipped-left>
      <v-toolbar-side-icon @click="drawer = !drawer"></v-toolbar-side-icon>
      <span class="title ml-3 mr-5">
        <router-link to="/" tag="span">Brewmeister</router-link>
      </span>
      <v-text-field solo-inverted flat hide-details label="Search" prepend-inner-icon="search"></v-text-field>
      <v-spacer></v-spacer>
      <sensor-widget :readings="readings" />
    </v-toolbar>
    <v-content>
      <v-container fluid fill-height class="grey lighten-4">
        <v-layout justify-center align-center>
          <v-flex shrink>
            <router-view />
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import SensorWidget from "@/components/SensorWidget";

import _ from 'lodash'

export default {
  data: () => ({
    drawer: null,
    items: [
      { icon: "lightbulb_outline", text: "About", to: "about" },
      { icon: "touch_app", text: "Helper widgets", to: "widgets" },
      { divider: true },
      { heading: "Brew Process" },
      { icon: "settings", text: "Current process", to: "process-monitor" },
      { heading: "Recipes" },
      { icon: "archive", text: "Recipes", to: "recipes" }
    ]
  }),
  props: {
    source: String
  },
  computed: {
    readings() {
      return _.get(this, '$store.state.sensors')
    }
  },
  components: {
    SensorWidget
  }
};
</script>

<style lang="scss">
#keep {
  .v-navigation-drawer__border {
    display: none;
  }
}
</style>