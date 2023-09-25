import { render } from 'preact';
import { useEffect, useState } from 'preact/hooks';

import './style.css';

import { merge } from 'lodash';

const Item = ({ item, index, items }) => {
    if (!item) {
        return null; // Return null if item is undefined
    }

    const timeDifference = index === 0 ? 0 : Date.parse(item.collection_time) - Date.parse(items[index - 1].collection_time);

    const formattedTimeDifference = timeDifference / 1000;

    return (
        <div>
            <a class={'item ' + (item ? 'active' : '')} href={item.url} target="_blank">
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
    <div>{id}</div>
    <div class="items">
        {
            Array(20).fill().map((_, index) => <Item items={job['items']} index={index} item={job['items'][index]} />)
        }
    </div>
    <div class="steps">
        <div class={"step " + (deep_get(job, 'steps.process_batch.end') ? 'done' : '')}>process</div>
        <div class={"step " + (deep_get(job, 'steps.ipfs_upload.end') ? 'done' : '')}>upload</div>
        <div class={"step " + (deep_get(job, 'steps.filter.end') ? 'done' : '')}>filter</div>
        <div class={"step " + (deep_get(job, 'steps.send_spot') ? 'done' : '')}>send</div>
        <div class={"step " + (deep_get(job, 'steps.receipt.start') ? 'start' : '') + " " + (deep_get(job, 'steps.receipt.value') ? 'done' : '')}>receipt</div>
    </div>
</div>;

const Collection = () => {
    return <div class="collection">
    </div>
}
const Intent = ({ id, intent, intents, intents_keys, index }) => {
    const timeDifference = index === intents_keys.length - 1 ? '' : Date.parse(intent.start) - Date.parse(intents[intents_keys[index + 1]].start)
    return <div class="intent">
        <div>
            <span class="intent_diff">{timeDifference / 1000}</span>
            <span class="intent_date">{intent.start}</span>
        </div>
        <div>{id}</div>
        <div>{intent.collections ? `${Object.keys(intent.collections).length} clct` : '0 clct'}</div>
        <div>{intent.errors ? `${Object.keys(intent.errors).length} err` : '0 err'}</div>
        <div class="module">{intent.module}</div>
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

export function App() {
    const [messages, setMessages] = useState([]);
    const [connected, setConnection] = useState(false);
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
        socket = new WebSocket('ws://localhost:8080/ws'); // Replace with your server's WebSocket URL
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
    const error_displayed = are_error_displayed ? '0fr 1fr' : '1fr 0fr';
    const layout_style = {
        background: connected ? "#4E937A" : "#B4656F",
        'grid-template-rows': (are_messages_displayed ? '1.0fr 2.5fr ' + '90px 0fr ' : '1.0fr 0fr ' + (is_filter_displayed ? ' 90px 1fr' : ' 90px 0fr')),
        'grid-template-columns': is_matrix_displayed ? '0fr 0fr 1fr 1fr 0fr' : error_displayed + ' 0fr 0fr 1fr'
    }
    const reversed_messages = [...messages].reverse();

    const intents = state['intents'] ? state['intents'] : {};
    const intents_keys = Object.keys(intents);
    const job_keys = Object.keys(jobs)
    intents_keys.reverse();
    job_keys.reverse();
    const domains = state['weights'] ? Object.keys(state['weights']) : []
    return (
        <div class="layout" style={layout_style}>
            <div class={"jobs "}>
                <div id="jobs">
                    {
                        job_keys.map((key) => <Job id={key} job={jobs[key]} />)
                    }
                </div>
            </div>
            <div class={"errors " + (are_error_displayed ? "active" : "inactive")}>
                { 
                    state['errors'] ? Object.keys(state['errors']).map((key) => <div class="errblock">
                        <div>{key}</div>
                        {state['errors'][key]['traceback'].map((value) => <div class="fullline">{value}</div>)}
                </div>) : <div />}
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
                <button id="errors" class={"rawbtn " + (are_error_displayed ? "active" : "")} onClick={() => setErrorDisplay(!are_error_displayed)} disabled={state['errors'] && Object.keys(state['errors']).length !== 0 ? false : true } > {state['errors'] ? Object.keys(state['errors']).length : 0} ERR</button>
                <button class={"rawbtn " + (are_messages_displayed ? "active" : "")} onClick={() => { setMessagesDisplay(!are_messages_displayed) }} disabled={is_matrix_displayed ? true : ''} >{messages.length} LOG</button>
                <button class={"rawbtn " + (is_matrix_displayed ? "active" : "")} onClick={() => { setMatrixDisplay(!is_matrix_displayed); setMessagesDisplay(false); setFilterDisplay(false) }}>
                    <svg height="48" viewBox="0 -960 960 960" width="48"><path d="M427-120v-225h60v83h353v60H487v82h-60Zm-307-82v-60h247v60H120Zm187-166v-82H120v-60h187v-84h60v226h-60Zm120-82v-60h413v60H427Zm166-165v-225h60v82h187v60H653v83h-60Zm-473-83v-60h413v60H120Z" /></svg>
                    <div>MATRIX</div>
                </button>
                <div class="group">
                    <button disabled={is_matrix_displayed ? true : !state['receipt'] || state['receipt'].length === 0 ? true : false} class="filterbtn rawbtn" >
                        {Object.keys(jobs).length - (state['receipt'] ? Object.keys(state['receipt']).length : 0)} MISS
                    </button>
                    <div class="separator rawbtn">=</div>
                    <button disabled={is_matrix_displayed ? true : !state['receipt'] || state['receipt'].length === 0 ? true : false} class="filterbtn rawbtn" >
                        {state['receipt'] ? Object.keys(state['receipt']).length : 0} REC
                    </button>
                    <div class="separator rawbtn">-</div>
                    <button disabled={is_matrix_displayed ? true : Object.keys(jobs).length === 0 ? true : false } class="rawbtn"  >
                        {jobs ? Object.keys(jobs).length : 0} JOBS
                    </button>
                </div>
                <button disabled={is_matrix_displayed ? true : !state['modules'] || state['modules'].length === 0 ? true : false} class="filterbtn rawbtn" onClick={() => setFilterDisplay(!is_filter_displayed)} >
                    {state['modules'] ? Object.keys(state['modules']).length : 0} SCRAPERS
                </button>

            </div>
            <div class={"filter " + (is_filter_displayed ? "active" : "inactive")}>
                {
                    state['modules'] ? Object.keys(state['modules']).map((key) => <div class="module">{key}</div>) : ''
                }
            </div>
        </div>
    );
}

render(<App />, document.getElementById('app'));
