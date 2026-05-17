
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
    return (
        scores.map((student) => (
  <div key={student.student_id} style={{backgroundColor: mapColor(student.score)}}>
    <h3>{student.student_id}</h3>
    <p>{student.score}</p>
  </div>
))
    );
}