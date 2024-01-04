import {baseRequest} from "./baseRequest";
import {serverResponses} from "../types/ServerResponseEnum";

export const loadCodeDB = async (index: string): Promise<{ success: boolean, message: any }> => {
    const result = await baseRequest("/database/load", {index})
    if (result.status === serverResponses.success) {
        return {success: true, message: result.response.code}
    } else {
        return {success: false, message: result.response}
    }
}