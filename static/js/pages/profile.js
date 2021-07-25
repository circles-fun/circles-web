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
        this.LoadProfileData("std", "vn");
        this.LoadAllofdata();
    },
    methods: {
        LoadAllofdata() {
            this.LoadMostBeatmaps();
            this.LoadScores('best');
            this.LoadScores('recent');
            this.LoadGrades();
            this.getGlobalRank();
            this.getCountryRank();
        },
        GettingUrl() {
            return `${window.location.protocol}//${window.location.hostname}:${window.location.port}`
        },
        LoadProfileData(mode, mods) {
            var vm = this;
            vm.$axios.get(`${this.GettingUrl()}/gw_api/get_user_info`, {
                    params: {
                        id: vm.userid,
                        mode: mode,
                        mods: mods,
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
        getGlobalRank() {
            var vm = this;
            let res = vm.$axios.get(`${this.GettingUrl()}/gw_api/get_player_rank`, {
                params: {
                    userid: vm.userid,
                    mode: vm.mode,
                    mods: vm.mods,
                }
            })
            vm.data.ranking.global = `#${res.data.rank}`;
        },
        getCountryRank() {
            var vm = this;
            let res = vm.$axios.get(`${this.GettingUrl()}/gw_api/get_player_rank`, {
                params: {
                    userid: vm.userid,
                    mode: vm.mode,
                    mods: vm.mods,
                    country: vm.data.stats.country,
                }
            })
            vm.data.ranking.country = `#${res.data.rank}`;
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
            vm.limit[0] = 5;
            vm.limit[1] = 5;
            vm.limit[2] = 5;
            vm.LoadProfileData(mode, mods)
            vm.LoadAllofdata()
        },
        ShowMore(sort) {
            var vm = this;
            var limit = vm.limit[sort];
            limit += 5;
            vm.limit[sort] = limit;
            vm.LoadScores(sort);
        },
        addCommas(nStr) {
            nStr += '';
            x = nStr.split('.');
            x1 = x[0];
            x2 = x.length > 1 ? '.' + x[1] : '';
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
    computed: {}
});