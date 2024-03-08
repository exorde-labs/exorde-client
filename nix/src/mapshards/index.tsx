
import { Main } from './main';
import { SelfUpdate } from './self_update';
import { Spotting } from './spotting';
import { PrepareBatch } from './prepare_batch';
import { GetItem } from './get_item';
import { Generator } from './generator';
import { ChooseModule} from './choose_module';
import { Brain } from './brain';

const Frame = ({handleMouseDown, handleMouseUp, handleMouseMove, offset, toggle_window}) =>  <svg 
    onMouseDown={handleMouseDown}
    onMouseUp={handleMouseUp}
    onMouseMove={handleMouseMove}
  width="100%" height="200%" 
  style={{
    "touch-action": "none",
    "user-select": "none",
    "-webkit-user-drag": "none",
    "-webkit-tap-highlight-color": "rgba(0, 0, 0, 0);",
  }}

  data-element-id="Collaboration_0tw1r0s" class="">
  <g class="viewport" transform={
        "matrix(1,0,0,1," + offset.x + "," + offset.y +")"
      }>
    <g class="layer-djs-grid">
      <rect x="-49040" y="-48620" width="100000" height="100000" style="fill: url(&quot;#djs-grid-pattern-841250&quot;);"></rect>
    </g>
    <g class="layer-base"></g>
    <g class="layer-root-2" data-element-id="Collaboration_0tw1r0s">
      
      <Main toggle_window={toggle_window} />
      <SelfUpdate />
      <Spotting />
      <PrepareBatch />
      <GetItem />
      <Generator />
      <ChooseModule />
      <Brain />



    </g>

  </g>
  <defs>
    <pattern id="djs-grid-pattern-841250" width="10" height="10" patternUnits="userSpaceOnUse">
      <circle cx="0.5" cy="0.5" r="0.5" style="fill: rgb(204, 204, 204);"></circle>
    </pattern>
    <marker id="sequenceflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v" viewBox="0 0 20 20" refX="11" refY="10" markerWidth="10" markerHeight="10" orient="auto">
      <path d="M 1 5 L 11 10 L 1 15 Z" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 1px; fill: rgb(34, 36, 42);"></path>
    </marker>
    <marker id="messageflow-end-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v" viewBox="0 0 20 20" refX="8.5" refY="5" markerWidth="20" markerHeight="20" orient="auto">
      <path d="m 1 5 l 0 -3 l 7 3 l -7 3 z" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 1px; fill: white; stroke-dasharray: 10000, 1;"></path>
    </marker>
    <marker id="messageflow-start-white-hsl_225_10_15_-0h0ig4fw6sejk6amlrkr6zc6v" viewBox="0 0 20 20" refX="6" refY="6" markerWidth="20" markerHeight="20" orient="auto">
      <circle cx="6" cy="6" r="3.5" style="stroke-linecap: round; stroke-linejoin: round; stroke: rgb(34, 36, 42); stroke-width: 1px; fill: white; stroke-dasharray: 10000, 1;"></circle>
    </marker>
  </defs>
</svg>;

export { Frame }
