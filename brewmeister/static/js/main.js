var temperatureController = new Vue({
    el: '#temperature',
    data: {
      temperature: '',
      target: '',
    },
    computed: {
      niceTemperature: function () {
        return Math.round (this.temperature)
      },
      niceTarget: function () {
        return Math.round (this.target)
      },
    },
    watch: {
      target: function () {
        this.updateTarget ()
      }
    },
    methods: {
      readTemperature: function () {
        this.$http.get('/api/v1/temperature').then((response) => {
          return response.json()
        }).then((data) => {
          this.temperature = data.temperature
          this.target = data.target
        });
      },
      updateTarget: _.debounce(
        function () {
          this.$http.post('/api/v1/temperature', {target: this.target}).then((response) => {
            this.readTemperature ()
          }, (response) => {
            // error callback
          });
        },
        300
      )
    },
    created: function () {
      this.readTemperature ()
      this.timer = setInterval (this.readTemperature, 2500)
    }
})

var heatingController = new Vue({
    el: '#heating',
    data: {
      heating: false,
    },
    methods: {
      readStatus: function () {
        this.$http.get('/api/v1/heating').then((response) => {
          return response.json()
        }).then((data) => {
          this.heating = data
        });
      },
      toggleHeating: function () {
        this.$http.post('/api/v1/heating', {on: !this.heating}).then((response) => {
          this.readStatus ()
        }, (response) => {
          // error callback
        });
      },
    },
    created: function () {
      this.readStatus ()
      this.timer = setInterval (this.readStatus, 5000)
    }
})


var stirringController = new Vue({
    el: '#stirring',
    data: {
      stirring: false,
    },
    methods: {
      readStatus: function () {
        this.$http.get('/api/v1/stirrer').then((response) => {
          return response.json()
        }).then((data) => {
          this.stirring = data
        });
      },
      toggleStirring: function () {
        this.$http.post('/api/v1/stirrer', {on: !this.stirring}).then((response) => {
          this.readStatus ()
        }, (response) => {
          // error callback
        });
      },
    },
    created: function () {
      this.readStatus ()
      this.timer = setInterval (this.readStatus, 5000)
    }
})
