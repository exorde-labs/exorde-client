import { useState } from 'preact/hooks';
import { Frame } from '../mapshards';

const Map = () => {
    const [offset, setOffset] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const [startPos, setStartPos] = useState({ x: 0, y: 0 });
    const handleMouseDown = (e) => {
        setIsDragging(true);
        setStartPos({ x: e.clientX, y: e.clientY });
    };
    const handleMouseUp = () => { setIsDragging(false) };
    const handleMouseMove = (e) => {
        if (!isDragging) return;
        const dx = e.clientX - startPos.x;
        const dy = e.clientY - startPos.y;

        setOffset({ x: offset.x + dx, y: offset.y + dy });
        setStartPos({ x: e.clientX, y: e.clientY });
    };
    const [details_window, set_details_window] = useState(null);
   
    const toggle_window = (value?: string) => {
        if (value === undefined) {
          set_details_window(null);
          return;
        }
        if (details_window === value) {
          set_details_window(null);
        } else {
          set_details_window(value);
        }
    };

    return <>
        <Frame  // map shards are splitted due to their size
            toggle_window={toggle_window}
            handleMouseDown={handleMouseDown}
            handleMouseUp={handleMouseUp}
            handleMouseMove={handleMouseMove}
            offset={offset}
        />
        <div class="details" style={{ "height": details_window !== null ? "50%" : "0%"}}>
            <h1>Exorde-Client</h1>
        </div>
    </>
}

export function Home() {

	return (
		<>
            <Map />
		</>
	);
}
