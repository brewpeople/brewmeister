var app = new Vue({
    el: '#app',
    data: {
      temperature: '',
      target: '',
      heating: false,
      stirring: false,
      elapsed: 0,
      timer: '',
    },
    computed: {
      niceTemperature: function () {
        return Math.round (this.temperature)
      },
      niceTarget: function () {
        return Math.round (this.target)
      },
      niceElapsed: function () {
        var hours = Math.floor(this.elapsed / 3600);
        var minutes = Math.floor((this.elapsed - (hours * 3600)) / 60);
        var seconds = Math.floor(this.elapsed - (hours * 3600) - (minutes * 60));

        if (hours < 10)
            hours = '0' + hours

        if (minutes < 10)
            minutes = '0' + minutes

        if (seconds < 10)
            seconds = '0' + seconds

        return hours + ':' + minutes + ':' + seconds
      }
    },
    watch: {
      target: function () {
        this.updateTarget ()
      }
    },
    methods: {
      readStatus: function () {
        this.$http.get('/api/v1/temperature').then((response) => {
          return response.json()
        }).then((data) => {
          this.temperature = data.temperature
          this.target = data.target
        });

        this.$http.get('/api/v1/heating').then((response) => {
          return response.json()
        }).then((data) => {
          this.heating = data
        });

        this.$http.get('/api/v1/stirrer').then((response) => {
          return response.json()
        }).then((data) => {
          this.stirring = data
        });

        this.$http.get('/api/v1/timer').then((response) => {
          return response.json()
        }).then((data) => {
          this.elapsed = data
        });
      },
      toggleHeating: function () {
        this.$http.post('/api/v1/heating', {on: !this.heating}).then((response) => {
          this.readStatus ()
        }, (response) => {
          // error callback
        });
      },
      toggleStirring: function () {
        this.$http.post('/api/v1/stirrer', {on: !this.stirring}).then((response) => {
          this.readStatus ()
        }, (response) => {
          // error callback
        });
      },
      resetTimer: function() {
        this.$http.post('/api/v1/timer', {}).then((response) => {
          // okay
        }, (response) => {
          // error callback
        });
      },
      updateTarget: _.debounce(
        function () {
          this.$http.post('/api/v1/temperature', {target: this.target}).then((response) => {
            this.readStatus ()
          }, (response) => {
            // error callback
          });
        },
        300
      )
    },
    created: function () {
      this.readStatus ()
      this.timer = setInterval (this.readStatus, 5000)
    }
})
