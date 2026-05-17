
function mapColor(score) {
    if (score >= 0.7) {
        return "green";
    } else if (score >= 0.4) {
        return "orange";
    } else {
        return "red";
    }
}



export function StudentCards({ scores }) {
    if (!scores || !Array.isArray(scores) || scores.length === 0) {
        return <p>No student data available</p>;
    }
    return (
        scores.map((student) => (
  <div key={student.student_id || Math.random()} style={{backgroundColor: mapColor(student.score || 0)}}>
    <h3>{student.student_id || "Unknown"}</h3>
    <p>{(student.score || 0).toFixed(2)}</p>
  </div>
))
    );
}