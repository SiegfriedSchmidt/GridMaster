import axios from "axios";
import {ApiPath} from "../utils/ProjectConstants";
import {serverResponses} from "../types/ServerResponseEnum";
import {ServerStatuses} from "../serverStatuses/ServerStatuses";

export const baseRequest = async (url: string, data?: object): Promise<{ status: serverResponses, response: any }> => {
    try {
        const response = data ? await axios.post(`${ApiPath}${url}`, data) : await axios.get(`${ApiPath}${url}`)
        if (response.status === ServerStatuses.OK) {
            return {
                status: serverResponses.success,
                response: response.data
            }
        } else {
            return {
                status: serverResponses.handledError,
                response: response.data.message
            }
        }
    } catch (e) {
        return {status: serverResponses.unknownError, response: "The server is not responding!"}
        // if (e instanceof AxiosError) {}
    }
}