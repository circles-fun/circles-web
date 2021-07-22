new Vue({
    el: "#app",
    delimiters: ["<%", "%>"],
    data() {
        return {
            data: {
                ranking: {
                    history: [],
                    global: null,
                    country: null,
                },
                stats: {},
                grades: {},
                scores: {
                    recent: {},
                    best: {},
                    most: {},
                    load: [false, false, false]
                },
            },
            mode: mode, // Getting from URL
            mods: mods, // Getting from URL
            userid: userid, // Getting from URL
            limit: [5, 5, 5],
        }
    },
    created() {
        // starting a page
        this.LoadProfileData()
        this.LoadAllofdata()
    },
    methods: {
        LoadAllofdata() {
            this.LoadMostBeatmaps()
            this.LoadScores('best');
            this.LoadScores('recent');
            this.LoadGrades();
            this.getRankHistory();
            this.getRank();
        },
        GettingUrl() {
            return `${window.location.protocol}//${window.location.hostname}:${window.location.port}`
        },
        LoadProfileData() {
            var vm = this;
            vm.$axios.get(`${this.GettingUrl()}/gw_api/get_user_info`, {
                params: {
                    id: vm.userid,
                }
            })
                .then(function (response) {
                    vm.data.stats = response.data.userdata;
                });
        },
        LoadGrades() {
            var vm = this;
            vm.$axios.get(`${this.GettingUrl()}/gw_api/get_user_grade`, {
                params: {
                    id: vm.userid,
                    mode: vm.mode,
                    mods: vm.mods,
                }
            })
                .then(function (response) {
                    vm.data.grades = response.data;
                });
        },
        async getRank() {
            var vm = this;
                    let res = await vm.$axios.get(`${this.GettingUrl()}/gw_api/get_player_rank`, {
                        params: {
                            userid: vm.userid,
                            mode: vm.mode,
                            mods: vm.mods,
                        }
                    })
                    vm.data.ranking.global = `#${res.data.global_rank}`;
                    vm.data.ranking.country = `#${res.data.country_rank}`
        },
        async getRankHistory() {
            var vm = this;
                    let res = await vm.$axios.get(`https://osu.circles.fun/api/get_player_rank_history`, {
                        params: {
                            userid: vm.userid,
                            mode: vm.mode,
                            mods: vm.mods,
                        }
                    })
                    vm.data.ranking.history = `#${res.data.history}`;
        },
        LoadScores(sort) {
            var vm = this;
            let type;
            switch (sort) {
                case 'best':
                    type = 0
                    break;
                case 'recent':
                    type = 1
                    break;
                default:
            }
            vm.data.scores.load[type] = true
            vm.$axios.get(`${this.GettingUrl()}/gw_api/get_player_scores`, {
                params: {
                    id: vm.userid,
                    mode: vm.mode,
                    mods: vm.mods,
                    sort: sort,
                    limit: vm.limit[type]
                }
            })
                .then(function (response) {
                    vm.data.scores[sort] = response.data.scores;
                    vm.data.scores.load[type] = false
                    console.log(vm.data.scores.load)
                });
        },
        LoadMostBeatmaps() {
            var vm = this;
            vm.data.scores.load[2] = true
            vm.$axios.get(`${this.GettingUrl()}/gw_api/get_player_most`, {
                params: {
                    id: vm.userid,
                    mode: vm.mode,
                    mods: vm.mods,
                    limit: vm.limit[2]
                }
            })
                .then(function (response) {
                    vm.data.scores.most = response.data.maps;
                    vm.data.scores.load[2] = false
                });
        },
        ChangeModeMods(mode, mods) {
            var vm = this;
            if (window.event) {
                window.event.preventDefault();
            }
            vm.mode = mode;
            vm.mods = mods;
            vm.limit[0] = 5
            vm.limit[1] = 5
            vm.limit[2] = 5
            vm.LoadAllofdata()
        },
        ShowMore(sort) {
            var vm = this;
            if (window.event) {
                window.event.preventDefault();
            }

            switch (sort) {
                case 'best':
                    vm.limit[0] = vm.limit[0] + 5
                    vm.LoadScores('best')
                    break;

                case 'recent':
                    vm.limit[1] = vm.limit[1] + 5
                    vm.LoadScores('recent')
                    break;

                case 'mostplayed':
                    vm.limit[2] = vm.limit[2] + 5
                    vm.LoadMostBeatmaps()
                    break;

                default:
                    break;
            }
        },
        addCommas(nStr) {
            nStr += '';
            var x = nStr.split('.');
            var x1 = x[0];
            var x2 = x.length > 1 ? '.' + x[1] : '';
            var rgx = /(\d+)(\d{3})/;
            while (rgx.test(x1)) {
                x1 = x1.replace(rgx, '$1' + ',' + '$2');
            }
            return x1 + x2;
        },
        secondsToDhm(seconds) {
            seconds = Number(seconds);
            var dDisplay = `${Math.floor(seconds / (3600 * 24))}d `;
            var hDisplay = `${Math.floor(seconds % (3600 * 24) / 3600)}h `;
            var mDisplay = `${Math.floor(seconds % 3600 / 60)}m `;
            return dDisplay + hDisplay + mDisplay;
        },
    },
    computed: {
    }
});