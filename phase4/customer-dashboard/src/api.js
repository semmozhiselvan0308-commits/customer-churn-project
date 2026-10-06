import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "X-API-Key": "mysecret123",
  },
});

export const getChurnSummary = () => {
  return API.get("/churn/summary");
};

export default API;
//re3
// export const getChurnSummary = () => {
//   return API.get("/churn/summary");
// };  