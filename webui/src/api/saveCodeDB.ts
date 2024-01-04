import {baseRequest} from "./baseRequest";
import {serverResponses} from "../types/ServerResponseEnum";

export const saveCodeDB = async (code: string): Promise<{ success: boolean, message: any }> => {
    const result = await baseRequest("/database/save", {code})
    if (result.status === serverResponses.success) {
        return {success: true, message: result.response.index}
    } else {
        return {success: false, message: result.response}
    }
}