import { useAttentionSocket } from '../hooks/useAttentionSocket';
import { useParams } from 'react-router-dom';
import {AttentionGauge} from '../components/AttentionGauge';
import {StudentCards} from '../components/StudentCards';


export default function LiveView() {
    const { sessionId } = useParams();
    const scores=useAttentionSocket(sessionId);
    return (
        <div>
        <h1>Live View</h1>
        <p>Session ID: {sessionId}</p>
        <AttentionGauge scores={scores} />
        <StudentCards scores={scores} />
        </div>
    );
}