from ..exceptions import UnexpectedState, NotReady, StateChangeError

UNSET = object()

STATES = {
    'queued' : '',
    'started' : '',
    'running' : '',
    'canceled' : '',
    'complete' : '',
    'DNF' : '',
}

RESULTS = {
    None : '',
    'PASS' : '',
    'FAIL' : '',
}

class Result():
    def __init__(self, caseRunConfiguration, state=None, result=None, final=False):
        self.caseRunConfiguration = caseRunConfiguration
        self.state = state
        self.result = result
        self.final = final

    def update(self, state=None, result=None, final=False):
        # TODO: Move code from CaseRunConfiguration.updateState here
        pass

    # TODO: define copy interface

class TestRuns():
    """Collection of case-run-configurations based on the Test Plans, Requirements and Test Cases from tclib provided library.

    This class also handles assignment of the workflows and manages their
    execution.
    """
    def __init__(self, library, event, config):
        self.caseRunConfigurations = []
        """List of CaseRunConfigurations taking part in this execution"""
        self.populateCaseRunConfigurations(library, event, config)
        self.assignWorkflows()
        self.resultsCollector = None # TODO: ResultsCollector(self.caseRunConfigurations)

    def populateCaseRunConfigurations(self, library, event, config):
        """
        Based on the event and config takes Test plans from library and
        for each of the Test plans collects list of Test cases and their
        configurations (in the context of the test plan). Based on those
        creates CaseRunConfiguration objects and stores them in
        caseRunConfigurations for later execution.

        If multiple caseRunConfiguration object share same testcase and
        configuration, they are merged into one object keeping records
        of the Test plans the case-run-configurations belong to.
        """

    def assignWorkflows(self):
        """
        Aggregate CaseRunConfiguration objects based on their workflows
        and call Workflows factory function which then takes care of creating
        desired Worklflow instances. The Workflow instances are responsible
        for assigning themselves (as they see fit) to the CaseRunConfiguration
        objects. Note that one Workflow can be assigned to multiple
        CaseRunConfiguration objects.

        :raises UnexpectedState: When there's at least one CaseRunConfiguration object without workflow assigned.
        :return: None
        :rtype: None
        """

    def start(self):
        """
        Run start method on all workflows assigned to the CaseRunConfiguration
        objects.

        Note there may be multiple CaseRunConfiguration objects sharing the
        same Workflow object. In such situation, the start method should be
        called for one Workflow object only once.

        If this start method was already successfully invoked, nothing should
        happen.

        :raises NotReady: When this method is called before workflows are assigned.
        :return: None
        :rtype: None
        """
        # TODO: notify ResultsCollector

    def wait(self):
        """
        Block execution until all workflows are finished. If this method is
        called after all workflows are finished, nothing should happen and no
        blocking should occur.

        :raises NotReady: When start method was not invoked yet.
        :return: None
        :rtype: None
        """
        # TODO: wait also for ResultsCollector (which should wait for all ResultsSenders)

class CaseRunConfiguration():
    """Representation of case-run-configuration containing logic for state and
    result management as well as information about workflow responsible for
    handling of the case-run-configuration.

    :param testcase: Test case for which the case-run is executed.
    :type testcase: tclib.structures.testcase.TestCase
    :param configuration: Configuration for which the case-run is executed.
    :type configuration: dict
    :param testplans: List of testplan ids for which the case-run-configuration executed.
    :type testplans: list
    """
    def __init__(self, testcase, configuration, testplans):
        self.testcase = testcase
        """TestCase handled by this run"""
        self.configuration = configuration
        """Configuration of the TestCase"""
        self.running_for = { testplan.id : True for testplan in testplans }
        """Mapping of plans for which this configuration shoud be executed"""
        self.workflow = None
        """Workflow instance handling execution of this configuration"""
        self.result = None
        """TODO"""
        # TODO: drop code below and use single result
        self.active = None
        """If None, there's no active workflow assigned. When True, changes of state and result are allowed."""
        self.state = None
        """State of the execution. Must be None or one of STATES"""
        self.result = None
        """Result of the execution. Must be None or one of RESULTS"""

    def cancel(self, reason, testplan_id=None):
        """
        Attempt to cancel this case-run-configuration either for all testplans
        or for specific testplan. The workflow cancel is invoked once there's
        no testplan for which the case-run-configuration would run.

        :param reason: Description why the cancel should happen.
        :type reason: str
        :param testplan_id: Identifier of the testplan for which the case-run-configuration should be canceled, defaults to None
        :type testplan_id: str, optional
        :raises StateChangeError: When attempting to cancel already canceled or in other way ended test-run-configuration
        :return: True if the workflow cancel was invoked
        :rtype: bool
        """
        if testplan_id is not None:
            self.running_for[testplan_id] = False
            if any(self.running_for.values()):
                return False
            self.workflow.cancel(self)
            # TODO: record reason
            self.updateState('canceled', None, True)
            return True
        else:
            for testplan_id in self.running_for:
                if self.cancel(reason, testplan_id):
                    return True
        raise UnexpectedState()

    def updateState(self, state, result=UNSET, final=False):
        """
        Update state of this case-run-configuration optionally setting result
        as well. This method is also used to mark the state as final effectively
        preventing any further change.

        :param state: Desired state to be set
        :type state: str
        :param result: Desired result to be set. If result is not set, the result is not changed. defaults to UNSET
        :type result: str, optional
        :param final: Mark the state as final preventing any future changes.
        :type final: bool
        :raises StateChangeError: When attempting to change state after final state was set.
        :raises ValueError: When unknown state or result is provided.
        :return: None
        :rtype: None
        """
        # TODO: lock when changing status
        self.result.update(state, result, final)
        # TODO: provide self.result.copy() to TestRun/ResultsCollector
        # TODO: move code below to Result
        if self.active is not None and self.active:
            raise StateChangeError('Cannot update status of already ended instance.')
        if state not in STATES:
            raise ValueError('Unknown state: "%s"' % state)
        self.state = state
        if result != UNSET:
            if result not in RESULTS:
                raise ValueError('Unknown result: "%s"' % result)
            self.result = result
        if final:
            self.active = False

    def assignWorkflow(self, workflow):
        """
        If workflow is already assigned and different workflow is about
        to assigned, raise traceback.

        While locked(state):
        If the state None, assign workflow and change state to queued.

        :param workflow: Mark this workflow as the one handling this case-run-configuration.
        :type workflow: tclib.Workflow
        :raises ValueError: When a different workflow instance is assigned.
        :return: None
        :rtype: None
        """

    def __iadd__(self, other):
        """
        Custom implementation of += operator.

        If the same CaseRunConfiguration is provided, update the information
        of Test Plans in this instance taking the Test Plans from the other
        instance.

        :raises NotImplemented: When object of incompatible type is given
        :raises ValueError: When not matching CaseRunConfiguration is given
        :return: self
        :rtype: CaseRunConfiguration
        """
        if not isinstance(other, CaseRunConfiguration):
            raise NotImplementedError()
        if self != other:
            raise ValueError("Cannot merge different CaseRunConfigurations")
        self.running_for.update(other.running_for)
        return self

    def __eq__(self, other):
        """
        Custom implementation of == operator.

        Compare with other CaseRunConfiguration and if they are of the same
        testcase and configuration return True.

        If the type of other is different fallback to other python methods
        allowing for other to still consider itself being the same thing.

        :raises NotImplemented:
        :return: True if the other CaseRunConfiguration is for the same testcase and has the same configuration, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, CaseRunConfiguration):
            raise NotImplementedError()
        return (self.testcase, self.configuration) == (other.testcase, other.configuration)