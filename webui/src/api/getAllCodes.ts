import {baseRequest} from "./baseRequest";
import {serverResponses} from "../types/ServerResponseEnum";

export const getAllCodes = async (): Promise<{ success: boolean, message: any }> => {
    const result = await baseRequest("/database/get_all")
    if (result.status === serverResponses.success) {
        return {success: true, message: result.response.all}
    } else {
        return {success: false, message: result.response}
    }
}