import { useContext } from "react";
import { AuthContext } from "../src/context/authContext";

export function useAuth() {
  return useContext(AuthContext);
}