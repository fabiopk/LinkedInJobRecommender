import axios from "axios";

export default axios.create({
  baseURL: `${window.location.protocol}//${window.location.hostname}/api`,
  timeout: 1000,
  headers: {
    "Access-Control-Allow-Origin": "*",
  },
});
