
const Main = ({toggle_window}) => <>
    <g class="djs-group">
        <g transform="matrix(1 0 0 1 165 320)">
            <rect id="main_status" x="0" y="0" width="1645" height="330" rx="0" ry="0" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 1.5px; fill: white; fill-opacity: 0.5;"></rect>
            <path style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 1.5px;" d="M30,0L30,330"></path>
            <text style="font-family: Arial, sans-serif; font-size: 12px; font-weight: normal; fill: rgb(34, 36, 42);" transform="matrix(-1.83697e-16 -1 1 -1.83697e-16 0 330)">
              <tspan x="152.0089282989502" y="18.6">main</tspan>
            </text>
        </g>
        <g transform="matrix(1 0 0 1 795 465)">
            <a onClick={(e) => { e.preventDefault(); e.stopImmediatePropagation(); toggle_window("verify_balance")}}>
                <rect x="0" y="0" width="100" height="80" rx="10" ry="10" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; fill: white; fill-opacity: 0.95;"></rect>
                <text style="font-family: Arial, sans-serif; font-size: 12px; font-weight: normal; fill: rgb(34, 36, 42);">
                  <tspan x="11.350444793701172" y="43.599999999999994">verify_balance</tspan>
                </text>
            </a>
        </g>
        <g transform="matrix(1 0 0 1 635 465)">
            <a id="get_static_configuration">
                <rect x="0" y="0" width="100" height="80" rx="10" ry="10" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; fill: white; fill-opacity: 0.95;"></rect>
                <text style="font-family: Arial, sans-serif; font-size: 12px; font-weight: normal; fill: rgb(34, 36, 42);">
                  <tspan x="9.565086364746094" y="36.4">get_static_conf</tspan>
                  <tspan x="27.008928298950195" y="50.8">iguration</tspan>
                </text>
            </a>
        </g>
        <g transform="matrix(1 0 0 1 475 465)">
            <a id="get_live_configuration">
                <rect x="0" y="0" width="100" height="80" rx="10" ry="10" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; fill: white; fill-opacity: 0.95;"></rect>
                <text style="font-family: Arial, sans-serif; font-size: 12px; font-weight: normal; fill: rgb(34, 36, 42);">
                  <tspan x="10.011157989501953" y="36.4">get_live_config</tspan>
                  <tspan x="31.67410659790039" y="50.8">uration</tspan>
                </text>
            </a>
        </g>
       
        <g transform="matrix(1 0 0 1 221 487)" id="main_start">
            <circle cx="18" cy="18" r="18" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; fill: white; fill-opacity: 0.95;"></circle>
        </g>
        <g id="main_while_true">
            <g transform="matrix(1 0 0 1 960 480)">
                <polygon points="25,0 50,25 25,50 0,25" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; fill: white; fill-opacity: 0.95;"></polygon>
                <path d="m 16,15 7.42857142857143,9.714285714285715 -7.42857142857143,9.714285714285715 3.428571428571429,0 5.714285714285715,-7.464228571428572 5.714285714285715,7.464228571428572 3.428571428571429,0 -7.42857142857143,-9.714285714285715 7.42857142857143,-9.714285714285715 -3.428571428571429,0 -5.714285714285715,7.464228571428572 -5.714285714285715,-7.464228571428572 -3.428571428571429,0 z" style="fill: rgb(34, 36, 42); stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 1px;"></path>
            </g>
            <g transform="matrix(1 0 0 1 961 456)">
                <text style="font-family: Arial, sans-serif; font-size: 11px; font-weight: normal; fill: rgb(34, 36, 42);">
                  <tspan x="0" y="9.899999999999999">while true</tspan>
                </text>
            </g>
        </g>

        <g data-element-id="Activity_17fbb3u" style="display: block;" transform="matrix(1 0 0 1 1075 465)">
            <a id="log_user_rep">
                <rect x="0" y="0" width="100" height="80" rx="10" ry="10" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; fill: white; fill-opacity: 0.95;"></rect>
                <text style="font-family: Arial, sans-serif; font-size: 12px; font-weight: normal; fill: rgb(34, 36, 42);">
                  <tspan x="15.011157989501953" y="43.599999999999994">log_user_rep</tspan>
                </text>
            </a>
        </g>
        <g transform="matrix(1 0 0 1 1245 465)">
            <a id="self_update">
                <rect x="0" y="0" width="100" height="80" rx="10" ry="10" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; fill: white; fill-opacity: 0.95;"></rect>
                <text style="font-family: Arial, sans-serif; font-size: 12px; font-weight: normal; fill: rgb(34, 36, 42);">
                  <tspan x="19.006694793701172" y="43.599999999999994">self_update</tspan>
                </text>
            </a>
        </g>
        <g transform="matrix(1 0 0 1 1405 465)">
            <a id="update_live_configuration">
                <rect x="0" y="0" width="100" height="80" rx="10" ry="10" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; fill: white; fill-opacity: 0.95;"></rect>
                <text style="font-family: Arial, sans-serif; font-size: 12px; font-weight: normal; fill: rgb(34, 36, 42);">
                  <tspan x="9.676338195800781" y="36.4">update_live_co</tspan>
                  <tspan x="22.008928298950195" y="50.8">nfiguration</tspan>
                </text>
            </a>
        </g>
        <g transform="matrix(1 0 0 1 1565 465)">
            <a id="run_job">
                <rect x="0" y="0" width="100" height="80" rx="10" ry="10" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; fill: white; fill-opacity: 0.95;"></rect>
                <text style="font-family: Arial, sans-serif; font-size: 12px; font-weight: normal; fill: rgb(34, 36, 42);">
                    <tspan x="30.005578994750977" y="43.599999999999994">
                        run_job
                    </tspan>
                </text>
            </a>
        </g>
        <g id="main_arrows">
            <path data-corner-radius="5" style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; marker-end: url(&quot;#sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v&quot;);" d="M735,505L795,505"></path>
            <path d="M735,505L795,505" class="djs-hit djs-hit-stroke" style="fill: none; stroke-opacity: 0; stroke: white; stroke-width: 15px;"></path>
            <rect x="729" y="499" rx="4" width="72" height="12" class="djs-outline" style="fill: none;"></rect>
            <path data-corner-radius="5" style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; marker-end: url(&quot;#sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v&quot;);" d="M895,505L960,505"></path>
            <path data-corner-radius="5" style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; marker-end: url(&quot;#sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v&quot;);" d="M575,505L635,505"></path>
            <path data-corner-radius="5" style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; marker-end: url(&quot;#sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v&quot;);" d="M257,505L475,505"></path>
            <path d="M415,505L475,505" class="djs-hit djs-hit-stroke" style="fill: none; stroke-opacity: 0; stroke: white; stroke-width: 15px;"></path>
            <path data-corner-radius="5" style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; marker-end: url(&quot;#sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v&quot;);" d="M1615,545L1615,630C1615,632.5,1612.5,635,1610,635L990,635C987.5,635,985,632.5,985,630L985,530"></path>
            <path data-corner-radius="5" style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; marker-end: url(&quot;#sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v&quot;);" d="M1010,505L1075,505"></path>
            <path d="M1010,505L1075,505" class="djs-hit djs-hit-stroke" style="fill: none; stroke-opacity: 0; stroke: white; stroke-width: 15px;"></path>
            <path data-corner-radius="5" style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; marker-end: url(&quot;#sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v&quot;);" d="M1175,505L1245,505"></path>
            <path d="M1175,505L1245,505" class="djs-hit djs-hit-stroke" style="fill: none; stroke-opacity: 0; stroke: white; stroke-width: 15px;"></path>
            <path data-corner-radius="5" style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; marker-end: url(&quot;#sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v&quot;);" d="M1345,505L1405,505"></path>
            <path d="M1345,505L1405,505" class="djs-hit djs-hit-stroke" style="fill: none; stroke-opacity: 0; stroke: white; stroke-width: 15px;"></path>
            <path data-corner-radius="5" style="fill: none; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 2px; marker-end: url(&quot;#sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v&quot;);" d="M1505,505L1565,505"></path>
            <path d="M1505,505L1565,505" class="djs-hit djs-hit-stroke" style="fill: none; stroke-opacity: 0; stroke: white; stroke-width: 15px;"></path>
            <path d="M1653,465L1682,435" class="djs-hit djs-hit-stroke" style="fill: none; stroke-opacity: 0; stroke: white; stroke-width: 15px;"></path>
        </g>
    </g>
</>
export { Main }
