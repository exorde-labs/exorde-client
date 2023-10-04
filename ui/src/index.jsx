import { render } from 'preact';
import { useEffect, useState } from 'preact/hooks';

import './style.css';

import { merge } from 'lodash';

const Item = ({ item, index, items }) => {
    if (!item) {
        return <div>
            <a class={'item'} >
                <div class="timedifference"></div>
            </a>
        </div>

    }
    const timeDifference = index === 0 ? 0 : items[index - 1] ? Date.parse(item.collection_time) - Date.parse(items[index - 1].collection_time) : 0;
    const formattedTimeDifference = timeDifference / 1000;
    return (
        <div>
            <a class={'item active'} href={item.url} target="_blank">
                <div class="timedifference">{formattedTimeDifference}</div>
                <div class="tooltip">
                    <p>{item['url']}</p>
                    <p>collected at: {item['collection_time']}</p>
                </div>
            </a>
        </div>
    );
};

function deep_get(obj, path) {
    const keys = path.split('.');
    let result = obj;

    for (const key of keys) {
        if (result && result.hasOwnProperty(key)) {
            result = result[key];
        } else {
            return undefined; // Property not found
        }
    }

    return result;
}

const Job = ({ id, job }) => <div class="job">
    <div class="title">
        {id} : <a href={"http://ipfs-gateway.exorde.network/ipfs/" + deep_get(job, 'steps.ipfs_upload.cid')} target="_blank">{deep_get(job, 'steps.ipfs_upload.cid')}</a> (<a href={"https://light-vast-diphda.explorer.mainnet.skalenodes.com/block/" + deep_get(job, 'steps.receipt.value') + "/transactions"} target="_blank">{deep_get(job, 'steps.receipt.value')}</a>)
    </div>
    <div class="items">
        {
            Array(15).fill().map((_, index) => <Item items={job['items']} index={index} item={job['items'] ? job['items'][index] : undefined} />)
        }
        <div class="">
            <a class="item item_count">
                <div>{deep_get(job, 'steps.ipfs_upload.count')}</div>
            </a>
        </div>
    </div>
    <div class="steps">
        <div class={"step " + (deep_get(job, 'steps.process_batch.start') ? 'start' : '') + " " + (deep_get(job, 'steps.process_batch.failed') ? 'failed' : '') + " " + (deep_get(job, 'steps.process_batch.end') ? 'done' : '')}>process <span>{deep_get(job, 'steps.process_batch.end') ? '(' + (Date.parse(deep_get(job, 'steps.process_batch.end')) - Date.parse(deep_get(job, 'steps.process_batch.start'))) / 1000 + 's)' : ''}</span></div>
        <div class={"step " + (deep_get(job, 'steps.ipfs_upload.start') ? 'start' : '') + " " + (deep_get(job, 'steps.ipfs_upload.failed') ? 'failed' : '') + " " + (deep_get(job, 'steps.ipfs_upload.end') ? ' done' : '')}>upload <span>{deep_get(job, 'steps.ipfs_upload.end') ? '(' + (Date.parse(deep_get(job, 'steps.ipfs_upload.end')) - Date.parse(deep_get(job, 'steps.ipfs_upload.start'))) / 1000 + 's)' : ''}</span></div>
        <div class={"step " + (deep_get(job, 'steps.filter.end') ? 'done' : '')}>filter</div>
        <div class={"step " + (deep_get(job, 'steps.send_spot') ? 'done' : '')}>send</div>
        <div class={"step " + (deep_get(job, 'steps.receipt.start') ? 'start' : '') + " " + (deep_get(job, 'steps.receipt.value') ? 'done' : '')  + " " + (deep_get(job, 'steps.receipt.failed') ? 'failed' : '') }>receipt  <span>{deep_get(job, 'steps.receipt.end') ? '(' + (Date.parse(deep_get(job, 'steps.receipt.end')) - Date.parse(deep_get(job, 'steps.receipt.start'))) / 1000 + 's)' : ''}</span> </div>
    </div>
</div>;



const Intent = ({ id, intent, intents, intents_keys, index }) => {
    const timeDifference = index === intents_keys.length - 1 ? '' : Date.parse(intent.start) - Date.parse(intents[intents_keys[index + 1]].start)
    const [open_keyword, setOpenKeyword] = useState(true);
    return <div class="intent_box">
        <div class="intent">
            <div>
                <span class="intent_diff">{timeDifference / 1000}</span>
                <button class="intent_keyword" onClick={() => setOpenKeyword(!open_keyword)} >{ intent.parameters ? intent.parameters.url_parameters.keyword : "" }</button>
                <span class="intent_date">{displayRelativeDate(Date.parse(intent.start))}</span>
            </div>
            <div>{intent.collections ? `${Object.keys(intent.collections).length} clct` : '0 clct'}</div>
            <div>{intent.errors ? `${Object.keys(intent.errors).length} err` : '0 err'}</div>
            <div class="module">{intent.module}</div>
        </div>
        <div class="ver">
            <div class="kw_details" style={open_keyword ? "height:100%": "0%"}>
                <span>Algorithm = {intent['keyword_alg'] }</span>
                <span>Roll = {intent['number'] }</span>
                <span>Threshold = {intent['cursor'] }</span>
                <span>Lang = {intent['lang']}</span>
                <span>Topic = {intent['topic']}</span>
                <span>Error = {intent['error'] ? 'true' : 'false'}</span>
            </div>
        </div>
    </div>
}
function shortenStringWithEllipsis(inputString, maxLength) {
    if (!inputString)
        return inputString
    if (inputString.length <= maxLength) {
        return inputString;
    }

    const leftHalfLength = Math.floor((maxLength - 3) / 2);
    const rightHalfLength = Math.ceil((maxLength - 3) / 2);

    const leftHalf = inputString.substring(0, leftHalfLength);
    const rightHalf = inputString.substring(inputString.length - rightHalfLength);

    return leftHalf + "..." + rightHalf;
}

function displayRelativeDate(targetDate) {
    const now = new Date();
    const diffInMilliseconds = now - targetDate;

    // Define time intervals in milliseconds
    const minute = 60 * 1000;
    const hour = minute * 60;
    const day = hour * 24;
    const week = day * 7;
    const month = day * 30; // Approximate

    if (diffInMilliseconds < minute) {
        return 'Just now';
    } else if (diffInMilliseconds < hour) {
        const minutesAgo = Math.floor(diffInMilliseconds / minute);
        return `${minutesAgo} minute${minutesAgo > 1 ? 's' : ''} ago`;
    } else if (diffInMilliseconds < day) {
        const hoursAgo = Math.floor(diffInMilliseconds / hour);
        return `${hoursAgo} hour${hoursAgo > 1 ? 's' : ''} ago`;
    } else if (diffInMilliseconds < week) {
        const daysAgo = Math.floor(diffInMilliseconds / day);
        return `${daysAgo} day${daysAgo > 1 ? 's' : ''} ago`;
    } else if (diffInMilliseconds < month) {
        const weeksAgo = Math.floor(diffInMilliseconds / week);
        return `${weeksAgo} week${weeksAgo > 1 ? 's' : ''} ago`;
    } else {
        const monthsAgo = Math.floor(diffInMilliseconds / month);
        return `${monthsAgo} month${monthsAgo > 1 ? 's' : ''} ago`;
    }
}

function Latest({ url, live_version, name, setTargetModule, targetModule }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const jsonData = await response.json();
                setData(jsonData);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        }

        fetchData();
    }, [url]);

    let response;
    if (loading) {
        response = 
            <div class="center">
                <h2>Loading...</h2>
            </div>
    }

    if (error) {
        response =
            <div class="center">
                <h2>{error.message}</h2>
        </div>;
    }
    if (!data) {
        response = <div class="center">
            <h2>No data available</h2>
        </div>;
    } else {
        response = <div>
            <div>latest : {data["tag_name"]}</div>
            <div>{displayRelativeDate(Date.parse(data["published_at"]))}</div>
            <div>{data["name"]}</div>
            <img src={data["author"]["avatar_url"]} class="author_pic" />
            <br />
            <br />
        </div>
    }
    return (
        <div class={"module latest " + (data ? data["tag_name"] !== live_version ? "error" : "" : "error")} onClick={() => {
            if (targetModule === name)
                setTargetModule(null)
            else
                setTargetModule(name)
        }}>
            <a target="_blank" href={"https://github.com/exorde-labs/" + name + "/blob/main/" + name + "/__init__.py"}>
                <svg width="98" height="96" viewBox="0 0 100 100" ><path fill-rule="evenodd" clip-rule="evenodd" d="M48.854 0C21.839 0 0 22 0 49.217c0 21.756 13.993 40.172 33.405 46.69 2.427.49 3.316-1.059 3.316-2.362 0-1.141-.08-5.052-.08-9.127-13.59 2.934-16.42-5.867-16.42-5.867-2.184-5.704-5.42-7.17-5.42-7.17-4.448-3.015.324-3.015.324-3.015 4.934.326 7.523 5.052 7.523 5.052 4.367 7.496 11.404 5.378 14.235 4.074.404-3.178 1.699-5.378 3.074-6.6-10.839-1.141-22.243-5.378-22.243-24.283 0-5.378 1.94-9.778 5.014-13.2-.485-1.222-2.184-6.275.486-13.038 0 0 4.125-1.304 13.426 5.052a46.97 46.97 0 0 1 12.214-1.63c4.125 0 8.33.571 12.213 1.63 9.302-6.356 13.427-5.052 13.427-5.052 2.67 6.763.97 11.816.485 13.038 3.155 3.422 5.015 7.822 5.015 13.2 0 18.905-11.404 23.06-22.324 24.283 1.78 1.548 3.316 4.481 3.316 9.126 0 6.6-.08 11.897-.08 13.526 0 1.304.89 2.853 3.316 2.364 19.412-6.52 33.405-24.935 33.405-46.691C97.707 22 75.788 0 48.854 0z" /></svg>
                <span>{name}</span>
            </a>
            <br />
            <br />
            <div class="used">{live_version}</div>
            <div class="lastmessage">{ response }</div>
        </div>
    );
}

const KeyWordSpread = ({state, targetModule}) => {
    const stats = {}
    let total = 0;
    if (state['modules'] && state['modules'][targetModule]) {
        for (const intent_id in state['modules'][targetModule]['intents']) {
            const keyword = state['modules'][targetModule]['intents'][intent_id].parameters.keyword
            if (keyword) {
                total += 1;
                if (!stats[keyword])
                    stats[keyword] = 1
                else
                    stats[keyword] = stats[keyword] + 1
            }
        }
    }
    return <div>
        {Object.keys(stats).map((key) => <div class="kw_stat">
            <div class="kw_value">{ stats[key] }</div>
            <div class="intent_keyword" >{ key }</div>
            <div class="kw_value" style="width:180px">{ ((stats[key] / total) * 100).toFixed(2) } %</div>
            <div class="progress_container" style="width:100%;">
                <div class="progress" style={{"width": ((stats[key] / total) * 100) + "%" }} />
            </div>
        </div>)}
    </div>
}

export function App() {
    const [messages, setMessages] = useState([]);
    const [connected, setConnection] = useState(false);
    const [targetModule, setTargetModule] = useState(null);
    const [state, setState] = useState({
        errors: {

        },
        statistics: {

        },
    })
    let socket = null;

    const [timeDifferenceInSeconds, setTimeDifferenceInSeconds] = useState(0);
    const [timeActiveInSeconds, setActiveTime] = useState(0);
    const [activity, setActivity] = useState([]);

    useEffect(() => {
        const interval = setInterval(() => {
            setTimeDifferenceInSeconds(timeDifferenceInSeconds + 1)
        }, 1000)

        return () => {
            clearInterval(interval);
        }
    })


    // Function to display a message in the HTML
    function displayMessage(message) {
        setMessages((prevMessages) => [...prevMessages, message]);
    }

    // Function to create a WebSocket connection
    function connectWebSocket() {
        socket = new WebSocket('ws://' + window.location.host + '/ws'); // Replace with your server's WebSocket URL
        // Handle incoming messages from the WebSocket server
        socket.addEventListener('message', (event) => {
            const message = event.data;
            const newData = merge(state, JSON.parse(message))
            setState((prevData) => newData);
            displayMessage(message);
            setTimeDifferenceInSeconds(0)
        });

        // Handle WebSocket connection open
        socket.addEventListener('open', (event) => {
            console.log('WebSocket connection opened');
            setConnection(true);
        });

        // Handle WebSocket connection close
        socket.addEventListener('close', (event) => {
            setConnection(false);
            if (event.wasClean) {
                console.log(`WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`);
            } else {
                console.log('WebSocket connection abruptly closed');
            }

            // Retry the connection after a delay (5 seconds)
            setTimeout(connectWebSocket, 5000);
        });

        // Handle WebSocket errors
        socket.addEventListener('error', (error) => {
            console.log(`WebSocket error: ${error.message}`);
        });
    }

    // Initial WebSocket connection on component mount
    useEffect(() => {
        connectWebSocket();

        // Clean up WebSocket
        return () => {
            if (socket) {
                socket.close();
            }
        };
    }, []);
    const jobs = state['jobs'] ? state['jobs'] : {}
    const [are_messages_displayed, setMessagesDisplay] = useState(false);
    const [is_matrix_displayed, setMatrixDisplay] = useState(false);
    const [is_filter_displayed, setFilterDisplay] = useState(false);
    const [are_error_displayed, setErrorDisplay] = useState(false);
    const error_displayed = are_error_displayed || targetModule !== null ? '0fr 1fr' : '1fr 0fr';
    const layout_style = {
        background: connected ? "#4E937A" : "#B4656F",
        'grid-template-rows': (are_messages_displayed ? '1.0fr 2.5fr ' + '90px 0fr ' : (is_filter_displayed ? '0fr 0fr 90px 1fr' : '1.0fr 0fr 90px 0fr')),
        'grid-template-columns': is_matrix_displayed ? '0fr 0fr 1fr 1fr 0fr' : error_displayed + ' 0fr 0fr 1fr'
    }
    const reversed_messages = [...messages].reverse();

    const intents = state['intents'] ? state['intents'] : {};
    const intents_keys = Object.keys(intents);
    const job_keys = Object.keys(jobs)
    intents_keys.reverse();
    job_keys.reverse();
    const domains = state['weights'] ? Object.keys(state['weights']) : []
    let module_requests = state['module_request'] ? Object.keys(state['module_request']) : []
    module_requests = module_requests.reverse()
    return (
        <div class="layout" style={layout_style}>
            <div class={"jobs " + (is_matrix_displayed ? "inactive" : "")}>
                <div id="jobs">
                    {
                        job_keys.map((key) => <Job id={key} job={jobs[key]} />)
                    }
                </div>
            </div>
            <div class={"errors " + (are_error_displayed ? "active" : "inactive")}>
                {
                    state['errors'] ? Object.keys(state['errors']).map((key) => <div class="errblock">
                        <div class="row">
                            <span>{key}</span>
                            <span>{state['errors'][key]['module']}</span>
                            <span>{Object.keys(state['errors'][key]['intents']).length}</span>
                        </div>
                        {state['errors'][key]['traceback'].map((value) => <div class="fullline">{value}</div>)}
                    </div>) : <div />
                }
            </div>
            <div class={"mat " + (is_matrix_displayed ? "active" : "inactive")}>
                <div class="matrix" id="brain">
                    <div class="cell label hlabel"></div>
                    <div class="cell label hlabel">quota</div>
                    <div class="cell label hlabel">weight</div>
                    <div class="cell label hlabel">focus</div>
                    <div class="cell label hlabel">enable</div>
                    {
                        [...domains].map((domain, index) => {
                            return <>
                                <div class="cell label vlabel">{domain}</div>
                                <div class="cell" />
                                <div class="cell">{state['weights'] ? state['weights'][domain] : ''}</div>
                                <div class="cell" />
                                <div class="cell" />
                            </>
                        })

                    }

                    <div class="cell label vlabel">other</div>
                    <div class="cell label vlabel" />
                    <div class="cell label vlabel" />
                    <div class="cell label vlabel" />
                    <div class="cell label vlabel" />
                </div>
                <div class="matrix" id="statistics">
                    <div class="cell label hlabel">24h</div>
                    <div class="cell label hlabel">1h</div>
                    <div class="cell label hlabel">30 items</div>
                    <div class="cell label hlabel">REP</div>
                    <div class="cell label hlabel"></div>
                    {
                        [...domains, 'other'].map((domain, index) => {
                            return <>
                                <div class="cell">{state['statistics'][domain] ? state['statistics'][domain]['24'] : ''}</div>
                                <div class="cell">{state['statistics'][domain] ? state['statistics'][domain]['1'] : ''}</div>
                                <div class="cell">{state['statistics'][domain] ? state['statistics'][domain]['30'] : ''}</div>
                                <div class="cell">{state['statistics'][domain] ? state['statistics'][domain]['rep'] : ''}</div>
                                <div class="cell" style="opacity:0" />
                            </>
                        })
                    }

                </div>
                <br style="margin-bottom:200px;" />
            </div>
            <div class="intents">
                {
                    intents_keys.map((key, index) => <Intent id={key} intent={intents[key]} intents_keys={intents_keys} index={index} intents={intents} />)
                }
            </div>
            <div class="raw">
                <div class="data">
                    <pre>
                        {JSON.stringify(state, null, 4)}
                    </pre>
                </div>
                <div class="messages">
                    <div id="messages">
                        {reversed_messages.map((message, index) => (
                            <pre>{message}</pre>
                        ))}
                    </div>
                </div>
            </div>
            <div class="status">
                <div class="left">
                    <div>{connected ? "connected" : "disconnected"}</div>
                    <div>{shortenStringWithEllipsis(reversed_messages[0], 100)}</div>
                    <div class="lastupdate">{timeDifferenceInSeconds} seconds ago</div>
                </div>
                <button id="errors" class={"rawbtn " + (are_error_displayed ? "active" : "")} onClick={() => setErrorDisplay(!are_error_displayed)} disabled={state['errors'] && Object.keys(state['errors']).length !== 0 ? false : true} > {state['errors'] ? Object.keys(state['errors']).length : 0} ERR</button>
                <button class={"rawbtn " + (are_messages_displayed ? "active" : "")} onClick={() => { setMessagesDisplay(!are_messages_displayed) }} disabled={is_matrix_displayed ? true : ''} >{messages.length} LOG</button>
                <button class={"rawbtn " + (is_matrix_displayed ? "active" : "")} onClick={() => { setMatrixDisplay(!is_matrix_displayed); setMessagesDisplay(false); setFilterDisplay(false) }}>
                    <svg height="48" viewBox="0 -960 960 960" width="48"><path d="M427-120v-225h60v83h353v60H487v82h-60Zm-307-82v-60h247v60H120Zm187-166v-82H120v-60h187v-84h60v226h-60Zm120-82v-60h413v60H427Zm166-165v-225h60v82h187v60H653v83h-60Zm-473-83v-60h413v60H120Z" /></svg>
                    <div>MATRIX</div>
                </button>
                <button disabled={is_matrix_displayed ? true : !state['modules'] || state['modules'].length === 0 ? true : false} class="filterbtn rawbtn" onClick={() => { setTargetModule(null); setFilterDisplay(!is_filter_displayed) }} >
                    {state['modules'] ? Object.keys(state['modules']).length : 0} SCRAPERS
                </button>
            </div>
            <div class={"updates " + (is_filter_displayed ? are_error_displayed || targetModule !== null ? "inactive" : "active" : "inactive")}>
                {module_requests.map((mod_req) => <div class="update">
                    <span class="title">{state['module_request'][mod_req]['module']}</span>
                    <span class="badge">{displayRelativeDate(Date.parse(state['module_request'][mod_req]['start']))}</span>
                    <span class="badge">L:{state['module_request'][mod_req]['local']}</span>
                    <span class="badge">O:{state['module_request'][mod_req]['online']}</span>
                </div>)}
            </div>
            <div class={"keywords " + (is_filter_displayed && are_error_displayed || targetModule !== null ? "active" : "inactive")}>
                <KeyWordSpread state={state} targetModule={targetModule} />
            </div>
            <div class={"filter " + (is_filter_displayed ? "active" : "inactive")}>
                {state['modules'] ? Object.keys(state['modules']).map(
                    (key) => <Latest targetModule={targetModule} setTargetModule={setTargetModule} url={"https://api.github.com/repos/exorde-labs/" + key + "/releases/latest"} live_version={state['modules'][key]['version']} name={key} />
                ) : ''}
            </div>
        </div>
    );
}

render(<App />, document.getElementById('app'));
