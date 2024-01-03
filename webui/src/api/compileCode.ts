import {baseRequest} from "./baseRequest";
import {serverResponses} from "../types/ServerResponseEnum";

export const compileCode = async (code: string): Promise<{ success: boolean, message: any }> => {
    const result = await baseRequest("/compile", {code})
    if (result.status === serverResponses.success) {
        return {success: true, message: result.response}
    } else {
        return {success: false, message: result.response}
    }
}