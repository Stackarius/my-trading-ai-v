def generate_explanation(analysis: dict) -> str:
    if 'signal' not in analysis or analysis['signal'] is None:
        return "No valid setup. HTF trend: {} | LTF confirm: No".format(analysis.get('trend', 'unknown'))
    
    sig = analysis['signal']
    reason = "HTF {} trend with BOS from valid Order Block. Price mitigated zone. LTF {} with liquidity sweep and FVG. RR: 1:{}.".format(
        analysis['trend'],
        analysis.get('ltf_mss', 'MSS'),
        sig['rr']
    )
    return "{} at {} | SL: {} | TP: {}. {}".format(
        sig['action'], sig['entry'], sig['sl'], sig['tp'], reason
    )
